import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_zap")


def test_add_liquidity(bob, zap, swap, underlying_coins, wrapped_coins, pool_token, initial_amounts, n_coins):
    zap.add_liquidity(initial_amounts, 0, {'from': bob})

    for wrapped, underlying, amount in zip(wrapped_coins, underlying_coins, initial_amounts):
        assert underlying.balanceOf(bob) == 0

        if wrapped == underlying:
            assert underlying.balanceOf(zap) == 0
            assert underlying.balanceOf(swap) == amount * 2
        else:
            assert underlying.balanceOf(zap) == 0
            assert underlying.balanceOf(swap) == 0
            assert wrapped.balanceOf(bob) == amount
            assert wrapped.balanceOf(zap) == 0
            assert wrapped.balanceOf(swap) == amount * 2

    assert pool_token.balanceOf(bob) == n_coins * 10**24
    assert pool_token.totalSupply() == n_coins * 10**24 * 2


def test_add_liquidity_with_slippage(bob, zap, pool_token, underlying_coins, underlying_decimals, n_coins):
    amounts = [10**i for i in underlying_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    zap.add_liquidity(amounts, 0, {'from': bob})

    for coin in underlying_coins:
        assert coin.balanceOf(zap) == 0

    assert 0.999 < pool_token.balanceOf(bob) / (n_coins * 10**18) < 1
    assert pool_token.balanceOf(zap) == 0


@pytest.mark.itercoins("idx")
def test_add_one_coin(bob, swap, zap, underlying_coins, wrapped_coins, pool_token, initial_amounts, idx, n_coins):
    amounts = [0] * n_coins
    amounts[idx] = initial_amounts[idx]
    zap.add_liquidity(amounts, 0, {'from': bob})

    zipped = zip(underlying_coins, wrapped_coins, amounts, initial_amounts)
    for underlying, wrapped, amount, initial in zipped:
        assert underlying.balanceOf(bob) == initial - amount

        if wrapped == underlying:
            assert underlying.balanceOf(zap) == 0
            assert underlying.balanceOf(swap) == amount + initial
        else:
            assert underlying.balanceOf(zap) == 0
            assert underlying.balanceOf(swap) == 0
            assert wrapped.balanceOf(bob) == initial
            assert wrapped.balanceOf(zap) == 0
            assert wrapped.balanceOf(swap) == amount + initial

    assert 0.999 < pool_token.balanceOf(bob) / 10**24 < 1
    assert pool_token.balanceOf(zap) == 0


def test_insufficient_balance(charlie, zap, underlying_decimals):
    amounts = [(10**i) for i in underlying_decimals]
    with brownie.reverts():
        zap.add_liquidity(amounts, 0, {'from': charlie})


@pytest.mark.parametrize("min_amount", [False, True])
def test_min_amount_too_high(alice, zap, underlying_decimals, min_amount, n_coins):

    amounts = [10**i for i in underlying_decimals]
    min_amount = n_coins * 10**18 + 1 if min_amount else 2**256 - 1
    with brownie.reverts():
        zap.add_liquidity(amounts, min_amount, {'from': alice})


def test_min_amount_with_slippage(bob, zap, underlying_decimals, n_coins):
    amounts = [10**i for i in underlying_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    with brownie.reverts():
        zap.add_liquidity(amounts, n_coins * 10**18, {'from': bob})
