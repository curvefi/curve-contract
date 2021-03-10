import pytest
from brownie import chain
from brownie.test import strategy

pytestmark = [
    pytest.mark.usefixtures("add_initial_liquidity"),
    pytest.mark.skip_pool("compound", "ib", "usdt", "ren", "sbtc"),
    pytest.mark.skip_meta,
]

ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


class StateMachine:
    """
    Stateful test that performs a series of deposits, swaps and withdrawals
    and confirms that the virtual price only goes up.
    """

    st_pct = strategy("decimal", min_value="0.5", max_value="1", places=2)
    st_rates = strategy("decimal[8]", min_value="1.001", max_value="1.004", places=4, unique=True)

    def __init__(cls, alice, swap, wrapped_coins, wrapped_decimals):
        cls.alice = alice
        cls.swap = swap
        cls.coins = wrapped_coins
        cls.decimals = wrapped_decimals
        cls.n_coins = len(wrapped_coins)

    def setup(self):
        # reset the virtual price between each test run
        self.virtual_price = self.swap.get_virtual_price()

    def _min_max(self):
        # get index values for the coins with the smallest and largest balances in the pool
        balances = [self.swap.balances(i) / (10 ** self.decimals[i]) for i in range(self.n_coins)]
        min_idx = balances.index(min(balances))
        max_idx = balances.index(max(balances))
        if min_idx == max_idx:
            min_idx = abs(min_idx - 1)

        return min_idx, max_idx

    def rule_ramp_A(self, st_pct):
        """
        Increase the amplification coefficient.

        This action happens at most once per test. If A has already
        been ramped, a swap is performed instead.
        """
        if not hasattr(self.swap, "ramp_A") or self.swap.future_A_time():
            return self.rule_exchange_underlying(st_pct)

        new_A = int(self.swap.A() * (1 + st_pct))
        self.swap.ramp_A(new_A, chain.time() + 86410, {"from": self.alice})

    def rule_increase_rates(self, st_rates):
        """
        Increase the stored rate for each wrapped coin.
        """
        for rate, coin in zip(self.coins, st_rates):
            if hasattr(coin, "set_exchange_rate"):
                coin.set_exchange_rate(int(coin.get_rate() * rate), {"from": self.alice})

    def rule_exchange(self, st_pct):
        """
        Perform a swap using wrapped coins.
        """
        send, recv = self._min_max()
        amount = int(10 ** self.decimals[send] * st_pct)
        value = amount if self.coins[send] == ETH_ADDRESS else 0
        self.swap.exchange(send, recv, amount, 0, {"from": self.alice, "value": value})

    def rule_exchange_underlying(self, st_pct):
        """
        Perform a swap using underlying coins.
        """
        if not hasattr(self.swap, "exchange_underlying"):
            # if underlying coins aren't available, use wrapped instead
            return self.rule_exchange(st_pct)

        send, recv = self._min_max()
        amount = int(10 ** self.decimals[send] * st_pct)
        value = amount if self.coins[send] == ETH_ADDRESS else 0
        self.swap.exchange_underlying(send, recv, amount, 0, {"from": self.alice, "value": value})

    def rule_remove_one_coin(self, st_pct):
        """
        Remove liquidity from the pool in only one coin.
        """
        if not hasattr(self.swap, "remove_liquidity_one_coin"):
            # not all pools include `remove_liquidity_one_coin`
            return self.rule_remove_imbalance(st_pct)

        idx = self._min_max()[1]
        amount = int(10 ** self.decimals[idx] * st_pct)
        self.swap.remove_liquidity_one_coin(amount, idx, 0, {"from": self.alice})

    def rule_remove_imbalance(self, st_pct):
        """
        Remove liquidity from the pool in an imbalanced manner.
        """
        idx = self._min_max()[1]
        amounts = [0] * self.n_coins
        amounts[idx] = 10 ** self.decimals[idx] * st_pct
        self.swap.remove_liquidity_imbalance(amounts, 2 ** 256 - 1, {"from": self.alice})

    def rule_remove(self, st_pct):
        """
        Remove liquidity from the pool.
        """
        amount = int(10 ** 18 * st_pct)
        self.swap.remove_liquidity(amount, [0] * self.n_coins, {"from": self.alice})

    def invariant_check_virtual_price(self):
        """
        Verify that the pool's virtual price has either increased or stayed the same.
        """
        virtual_price = self.swap.get_virtual_price()
        assert virtual_price >= self.virtual_price
        self.virtual_price = virtual_price

    def invariant_advance_time(self):
        """
        Advance the clock by 1 hour between each action.
        """
        chain.sleep(3600)


def test_number_always_go_up(
    add_initial_liquidity,
    state_machine,
    swap,
    alice,
    bob,
    underlying_coins,
    wrapped_coins,
    wrapped_decimals,
    base_amount,
    set_fees,
):
    set_fees(10 ** 7, 0)

    for underlying, wrapped in zip(underlying_coins, wrapped_coins):
        amount = 10 ** 18 * base_amount
        if underlying == ETH_ADDRESS:
            bob.transfer(alice, amount)
        else:
            underlying._mint_for_testing(alice, amount, {"from": alice})
        if underlying != wrapped:
            wrapped._mint_for_testing(alice, amount, {"from": alice})

    state_machine(
        StateMachine,
        alice,
        swap,
        wrapped_coins,
        wrapped_decimals,
        settings={"max_examples": 25, "stateful_step_count": 50},
    )
