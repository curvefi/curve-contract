import brownie
import pytest

pytestmark = pytest.mark.skip_pool("busd", "compound", "pax", "susd", "usdt", "y")


@pytest.fixture(scope="module", autouse=True)
def setup(alice, wrapped_coins, swap, initial_amounts):
    # mint (10**6 * precision) of each coin in the pool for alice and bob
    # alice provides all of her balances as the initial liquidity

    for coin, amount in zip(wrapped_coins, initial_amounts):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("divisor", [1, 5, 42])
def test_remove_one_coin(alice, swap, wrapped_coins, pool_token, idx, divisor, n_coins):
    amount = pool_token.balanceOf(alice) // divisor

    expected = swap.calc_withdraw_one_coin(amount, idx)
    swap.remove_liquidity_one_coin(amount, idx, 0, {'from': alice})

    assert wrapped_coins[idx].balanceOf(alice) == expected
    assert pool_token.balanceOf(alice) == n_coins * 10**24 - amount


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
