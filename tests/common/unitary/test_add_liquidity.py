import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, wrapped_coins, swap, initial_amounts):
    # mint (10**6 * precision) of each coin in the pool for alice and bob
    # alice provides all of her balances as the initial liquidity

    for coin, amount in zip(wrapped_coins, initial_amounts):
        for acct in (alice, bob):
            coin._mint_for_testing(acct, amount, {'from': acct})
            coin.approve(swap, 2**256-1, {'from': acct})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


def test_add_liquidity(bob, swap, wrapped_coins, pool_token, initial_amounts, n_coins):
    swap.add_liquidity(initial_amounts, 0, {'from': bob})

    for coin, amount in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(bob) == 0
        assert coin.balanceOf(swap) == amount * 2

    assert pool_token.balanceOf(bob) == n_coins * 10**24
    assert pool_token.totalSupply() == n_coins * 10**24 * 2


def test_add_liquidity_with_slippage(bob, swap, pool_token, wrapped_decimals, n_coins):
    amounts = [10**i for i in wrapped_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    swap.add_liquidity(amounts, 0, {'from': bob})

    assert 0.999 < pool_token.balanceOf(bob) / (n_coins * 10**18) < 1


@pytest.mark.itercoins("idx")
def test_add_one_coin(bob, swap, wrapped_coins, pool_token, initial_amounts, idx, n_coins):
    amounts = [0] * n_coins
    amounts[idx] = initial_amounts[idx]
    swap.add_liquidity(amounts, 0, {'from': bob})

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(bob) == initial_amounts[i] - amounts[i]
        assert coin.balanceOf(swap) == initial_amounts[i] + amounts[i]

    assert 0.999 < pool_token.balanceOf(bob) / 10**24 < 1


def test_insufficient_balance(charlie, swap, wrapped_decimals):
    amounts = [(10**i) for i in wrapped_decimals]
    with brownie.reverts():
        swap.add_liquidity(amounts, 0, {'from': charlie})


@pytest.mark.parametrize("min_amount", [3 * 10**18 + 1, 2**256-1])
def test_min_amount_too_high(alice, swap, wrapped_decimals, min_amount):
    amounts = [10**i for i in wrapped_decimals]
    with brownie.reverts():
        swap.add_liquidity(amounts, min_amount, {'from': alice})


def test_min_amount_with_slippage(bob, swap, wrapped_decimals, n_coins):
    amounts = [10**i for i in wrapped_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    with brownie.reverts("Slippage screwed you"):
        swap.add_liquidity(amounts, n_coins * 10**18, {'from': bob})
