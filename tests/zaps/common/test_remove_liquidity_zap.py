import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "approve_zap")


def test_remove_liquidity(
    alice,
    bob,
    swap,
    zap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    initial_amounts,
    n_coins,
):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {'from': alice})
    zap.remove_liquidity(n_coins * 10**24, [0] * n_coins, {'from': bob})

    zipped = zip(underlying_coins, wrapped_coins, initial_amounts)
    for underlying, wrapped, amount in zipped:
        assert underlying.balanceOf(zap) == 0
        assert wrapped.balanceOf(zap) == 0

        assert underlying.balanceOf(swap) == 0
        assert wrapped.balanceOf(swap) == 0
        assert 0 < underlying.balanceOf(bob) <= amount

    assert pool_token.balanceOf(bob) == 0
    assert pool_token.totalSupply() == 0


def test_remove_partial(
    alice, bob, swap, zap, underlying_coins, wrapped_coins, pool_token, initial_amounts, n_coins
):
    withdraw_amount = pool_token.balanceOf(alice) // 2
    pool_token.transfer(bob, pool_token.balanceOf(alice), {'from': alice})
    zap.remove_liquidity(withdraw_amount, [0] * n_coins, {'from': bob})

    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        assert underlying.balanceOf(zap) == 0
        assert wrapped.balanceOf(zap) == 0

        assert wrapped.balanceOf(swap) == amount // 2
        assert 0 < underlying.balanceOf(bob) <= amount // 2

    assert pool_token.balanceOf(zap) == 0
    assert pool_token.balanceOf(bob) == n_coins * 10**24 - withdraw_amount
    assert pool_token.totalSupply() == n_coins * 10**24 - withdraw_amount


@pytest.mark.itercoins("idx")
def test_below_min_amount(alice, zap, initial_amounts, n_coins, idx):
    min_amount = initial_amounts.copy()
    min_amount[idx] += 1

    with brownie.reverts():
        zap.remove_liquidity(n_coins * 10**24, min_amount, {'from': alice})


def test_amount_exceeds_balance(alice, zap, n_coins):
    with brownie.reverts():
        zap.remove_liquidity(n_coins * 10**24 + 1, [0] * n_coins, {'from': alice})
