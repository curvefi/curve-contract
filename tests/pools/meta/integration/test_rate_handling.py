import pytest
from brownie import ETH_ADDRESS, chain
from brownie.test import strategy

pytestmark = [pytest.mark.usefixtures("add_initial_liquidity")]


class StateMachine:
    """
    Stateful test that performs a series of deposits, swaps and withdrawals
    on a meta pool and confirms that the virtual price only goes up.
    """

    st_pct = strategy("decimal", min_value="0.5", max_value="1", places=2)
    st_rates = strategy("decimal[8]", min_value="1.001", max_value="1.004", places=4, unique=True)

    def __init__(
        cls,
        alice,
        base_swap,
        swap,
        wrapped_coins,
        wrapped_decimals,
        underlying_coins,
        underlying_decimals,
    ):
        cls.alice = alice
        cls.swap = swap
        cls.base_swap = base_swap
        cls.coins = wrapped_coins
        cls.decimals = wrapped_decimals
        cls.underlying_coins = underlying_coins
        cls.underlying_decimals = underlying_decimals
        cls.n_coins = len(wrapped_coins)

        # approve base pool for swaps
        base_coins = cls.underlying_coins[cls.n_coins - 1 :]
        for idx in range(len(base_coins)):
            base_coins[idx].approve(cls.base_swap, 2 ** 256 - 1, {"from": cls.alice})

    def setup(self):
        # reset the virtual price between each test run
        self.virtual_price_base = self.base_swap.get_virtual_price()
        self.virtual_price = self.swap.get_virtual_price()

    def _min_max(self):
        # get index values for the coins with the smallest and largest balances in the meta pool
        balances = [self.swap.balances(i) / (10 ** self.decimals[i]) for i in range(self.n_coins)]
        min_idx = balances.index(min(balances))
        max_idx = balances.index(max(balances))
        if min_idx == max_idx:
            min_idx = abs(min_idx - 1)

        return min_idx, max_idx

    def _min_max_underlying(self, base=False):
        # get index values for underlying coins with smallest and largest balances
        balances = []
        for i in range(len(self.underlying_coins)):
            if i < self.n_coins - 1:
                balances.append(self.swap.balances(i) / 10 ** self.underlying_decimals[i])
            else:
                base_i = i - (self.n_coins - 1)
                balances.append(
                    self.base_swap.balances(base_i) / (10 ** self.underlying_decimals[base_i])
                )

        if base:
            for i in range(self.n_coins - 1):
                balances.pop(0)

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
        if self.swap.future_A_time():
            return self.rule_exchange_underlying(st_pct)

        new_A = int(self.swap.A() * (1 + st_pct))
        self.swap.ramp_A(new_A, chain.time() + 86410, {"from": self.alice})

    def rule_increase_rates(self, st_pct):
        """
        Increase the virtual price of the base pool.
        """
        if not hasattr(self.base_swap, "donate_admin_fees"):
            # not all base pools include `donate_admin_fees`
            return self.rule_generate_fees()

        for i, coin in enumerate(self.underlying_coins):
            if i < self.n_coins - 1:
                continue
            amount = int(10 ** self.underlying_decimals[i] * (1 + st_pct))
            coin._mint_for_testing(self.base_swap, amount, {"from": self.alice})
        self.base_swap.donate_admin_fees()

    def rule_exchange(self, st_pct):
        """
        Perform a swap using wrapped coins.
        """
        send, recv = self._min_max()

        amount = int(10 ** self.decimals[send] * st_pct)
        value = amount if self.underlying_coins[send] == ETH_ADDRESS else 0
        self.swap.exchange(send, recv, amount, 0, {"from": self.alice, "value": value})

    def rule_generate_fees(self):
        """
        Pushes base pool to be heavily imbalanced and then rebalances it to generate a lot of fees
        and thereby increase the virtual price.
        """
        min_idx, max_idx = self._min_max_underlying(base=True)
        dx = self.base_swap.balances(max_idx)
        base_decimals = self.underlying_decimals[self.n_coins - 1 :]
        if base_decimals[max_idx] > base_decimals[min_idx]:
            dx = dx / 10 ** (base_decimals[max_idx] - base_decimals[min_idx])
        elif base_decimals[min_idx] > base_decimals[max_idx]:
            dx = dx * 10 ** (base_decimals[min_idx] - base_decimals[max_idx])

        base_coins = self.underlying_coins[self.n_coins - 1 :]
        base_coins[min_idx]._mint_for_testing(self.alice, dx, {"from": self.alice})

        tx = self.base_swap.exchange(min_idx, max_idx, dx, 0, {"from": self.alice})
        dy = tx.events["TokenExchange"]["tokens_bought"]
        self.base_swap.exchange(max_idx, min_idx, dy, 0, {"from": self.alice})

    def rule_exchange_underlying(self, st_pct):
        """
        Perform a swap using underlying coins.
        """
        send, recv = self._min_max_underlying()

        amount = int(10 ** self.underlying_decimals[send] * st_pct)
        value = amount if self.underlying_coins[send] == ETH_ADDRESS else 0
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
        Verify that both the meta and the base pools' virtual prices have either
        increased or stayed the same.
        """
        virtual_price_base = self.base_swap.get_virtual_price()
        virtual_price = self.swap.get_virtual_price()
        assert virtual_price_base >= self.virtual_price_base
        assert virtual_price + 1 >= self.virtual_price
        self.virtual_price_base = virtual_price_base
        self.virtual_price = virtual_price

    def invariant_advance_time(self):
        """
        Advance the clock by 1 hour between each action.
        """
        chain.sleep(3600)


def test_number_always_go_up(
    add_initial_liquidity,
    state_machine,
    base_swap,
    swap,
    alice,
    bob,
    underlying_coins,
    underlying_decimals,
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
        base_swap,
        swap,
        wrapped_coins,
        wrapped_decimals,
        underlying_coins,
        underlying_decimals,
        settings={"max_examples": 25, "stateful_step_count": 50},
    )
