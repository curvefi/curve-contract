import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob")


def test_add_liquidity(
    bob, swap, underlying_coins, wrapped_coins, pool_token, initial_amounts, base_amount, n_coins
):
    swap.add_liquidity(initial_amounts, 0, True, {"from": bob})

    for coin in underlying_coins:
        assert coin.balanceOf(bob) == 0
        assert coin.balanceOf(swap) == 0

    for coin, amount in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(bob) == amount
        assert coin.balanceOf(swap) == amount * 2

    assert pool_token.balanceOf(bob) == n_coins * 10 ** 18 * base_amount
    assert pool_token.totalSupply() == n_coins * 10 ** 18 * base_amount * 2


def test_add_liquidity_with_slippage(bob, swap, pool_token, wrapped_decimals, n_coins):
    amounts = [10 ** i for i in wrapped_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    swap.add_liquidity(amounts, 0, True, {"from": bob})

    assert 0.999 < pool_token.balanceOf(bob) / (n_coins * 10 ** 18) < 1


@pytest.mark.itercoins("idx")
def test_add_one_coin(
    bob,
    swap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    initial_amounts,
    base_amount,
    idx,
    n_coins,
):
    amounts = [0] * n_coins
    amounts[idx] = initial_amounts[idx]
    swap.add_liquidity(amounts, 0, True, {"from": bob})

    for i, coin in enumerate(underlying_coins):
        assert coin.balanceOf(bob) == initial_amounts[i] - amounts[i]
        assert coin.balanceOf(swap) == 0

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(bob) == initial_amounts[i]
        assert coin.balanceOf(swap) == initial_amounts[i] + amounts[i]

    assert 0.999 < pool_token.balanceOf(bob) / (10 ** 18 * base_amount) < 1


def test_insufficient_balance(charlie, swap, underlying_decimals):
    amounts = [(10 ** i) for i in underlying_decimals]
    with brownie.reverts():
        swap.add_liquidity(amounts, 0, True, {"from": charlie})


@pytest.mark.parametrize("min_amount", [3 * 10 ** 18 + 1, 2 ** 256 - 1])
def test_min_amount_too_high(alice, swap, underlying_decimals, min_amount):
    amounts = [10 ** i for i in underlying_decimals]
    with brownie.reverts():
        swap.add_liquidity(amounts, min_amount, True, {"from": alice})


def test_min_amount_with_slippage(bob, swap, underlying_decimals, n_coins):
    amounts = [10 ** i for i in underlying_decimals]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    with brownie.reverts("Slippage screwed you"):
        swap.add_liquidity(amounts, n_coins * 10 ** 18, True, {"from": bob})
