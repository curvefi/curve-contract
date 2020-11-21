import brownie
import pytest
from simulation import Curve

pytestmark = [
    pytest.mark.skip_pool("busd", "compound", "pax", "susd", "usdt", "y"),
    pytest.mark.usefixtures("add_initial_liquidity"),
]


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("rate_mod", [0.9, 0.99, 1.01, 1.1])
@pytest.mark.skip_pool("ren", "sbtc")
def test_amount_received(chain, alice, swap, wrapped_coins, wrapped_decimals, idx, rate_mod):

    decimals = wrapped_decimals[idx]
    wrapped = wrapped_coins[idx]

    if hasattr(wrapped, 'set_exchange_rate'):
        wrapped.set_exchange_rate(int(wrapped.get_rate() * rate_mod), {'from': alice})
        # time travel so rates take effect in pools that use rate caching
        chain.sleep(3600)
    else:
        rate_mod = 1.00001

    swap.remove_liquidity_one_coin(10**18, idx, 0, {'from': alice})

    if rate_mod < 1:
        assert 10**decimals <= wrapped.balanceOf(alice) < 10**decimals / rate_mod
    else:
        assert 10**decimals // rate_mod <= wrapped.balanceOf(alice) <= 10**decimals


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("divisor", [1, 5, 42])
def test_lp_token_balance(alice, swap, pool_token, idx, divisor, n_coins, base_amount):
    amount = pool_token.balanceOf(alice) // divisor

    swap.remove_liquidity_one_coin(amount, idx, 0, {'from': alice})

    assert pool_token.balanceOf(alice) == n_coins * 10**18 * base_amount - amount


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("rate_mod", [0.9, 1.1])
def test_expected_vs_actual(chain, alice, swap, wrapped_coins, pool_token, idx, rate_mod):
    amount = pool_token.balanceOf(alice) // 10
    wrapped = wrapped_coins[idx]

    if hasattr(wrapped, 'set_exchange_rate'):
        wrapped.set_exchange_rate(int(wrapped.get_rate() * rate_mod), {'from': alice})
        # time travel so rates take effect in pools that use rate caching
        chain.sleep(3600)
        chain.mine()

    expected = swap.calc_withdraw_one_coin(amount, idx)
    swap.remove_liquidity_one_coin(amount, idx, 0, {'from': alice})

    assert wrapped_coins[idx].balanceOf(alice) == expected


@pytest.mark.itercoins("idx")
def test_below_min_amount(alice, swap, wrapped_coins, pool_token, idx):
    amount = pool_token.balanceOf(alice)

    expected = swap.calc_withdraw_one_coin(amount, idx)
    with brownie.reverts():
        swap.remove_liquidity_one_coin(amount, idx, expected+1, {'from': alice})


@pytest.mark.itercoins("idx")
def test_amount_exceeds_balance(bob, swap, wrapped_coins, pool_token, idx):
    with brownie.reverts():
        swap.remove_liquidity_one_coin(1, idx, 0, {'from': bob})


def test_below_zero(alice, swap):
    with brownie.reverts():
        swap.remove_liquidity_one_coin(1, -1, 0, {'from': alice})


def test_above_n_coins(alice, swap, wrapped_coins, n_coins):
    with brownie.reverts():
        swap.remove_liquidity_one_coin(1, n_coins, 0, {'from': alice})

@pytest.mark.itercoins("idx")
def test_against_simulation(alice, swap, n_coins, pool_token, idx):
    amount = pool_token.balanceOf(alice)

    balances = [swap.balances(i) for i in range(n_coins)]
    curve_model = Curve(swap.A(), balances, n_coins, tokens=pool_token.totalSupply())
    expected, _ = curve_model.calc_withdraw_one_coin(amount, idx)

    assert swap.swap.calc_withdraw_one_coin(amount, idx) == expected
