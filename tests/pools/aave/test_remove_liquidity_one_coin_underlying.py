import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(add_initial_liquidity, alice, bob, pool_token):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})


@pytest.mark.itercoins("idx")
def test_amount_received(chain, bob, swap, underlying_coins, wrapped_coins, wrapped_decimals, idx):

    decimals = wrapped_decimals[idx]
    wrapped = wrapped_coins[idx]
    underlying = underlying_coins[idx]

    initial = wrapped.balanceOf(swap)

    swap.remove_liquidity_one_coin(10 ** 18, idx, 0, True, {"from": bob})

    assert 0.9999 < underlying.balanceOf(bob) / 10 ** decimals < 1
    assert wrapped.balanceOf(swap) + underlying.balanceOf(bob) == initial


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("divisor", [1, 5, 42])
def test_lp_token_balance(bob, swap, pool_token, idx, divisor, n_coins, base_amount):
    amount = pool_token.balanceOf(bob) // divisor

    swap.remove_liquidity_one_coin(amount, idx, 0, True, {"from": bob})

    assert pool_token.balanceOf(bob) == n_coins * 10 ** 18 * base_amount - amount


@pytest.mark.itercoins("idx")
@pytest.mark.parametrize("rate_mod", [0.9, 1.1])
def test_expected_vs_actual(chain, bob, swap, underlying_coins, pool_token, idx, rate_mod):
    amount = pool_token.balanceOf(bob) // 10

    expected = swap.calc_withdraw_one_coin(amount, idx)
    swap.remove_liquidity_one_coin(amount, idx, 0, True, {"from": bob})

    assert underlying_coins[idx].balanceOf(bob) == expected


@pytest.mark.itercoins("idx")
def test_below_min_amount(bob, swap, wrapped_coins, pool_token, idx):
    amount = pool_token.balanceOf(bob)

    expected = swap.calc_withdraw_one_coin(amount, idx)
    with brownie.reverts():
        swap.remove_liquidity_one_coin(amount, idx, expected + 1, True, {"from": bob})


@pytest.mark.itercoins("idx")
def test_amount_exceeds_balance(bob, swap, wrapped_coins, pool_token, idx):
    with brownie.reverts():
        swap.remove_liquidity_one_coin(pool_token.balanceOf(bob) + 1, idx, 0, True, {"from": bob})
