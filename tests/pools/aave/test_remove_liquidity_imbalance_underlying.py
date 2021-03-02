import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(add_initial_liquidity, alice, bob, pool_token):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})


@pytest.mark.parametrize("divisor", [2, 5, 10])
def test_remove_balanced(
    bob,
    swap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    divisor,
    initial_amounts,
    n_coins,
    base_amount,
):
    amounts = [i // divisor for i in initial_amounts]
    max_burn = (n_coins * 10 ** 18 * base_amount) // divisor
    swap.remove_liquidity_imbalance(amounts, max_burn + 1, True, {"from": bob})

    for i, coin in enumerate(underlying_coins):
        assert coin.balanceOf(bob) == amounts[i]
        assert coin.balanceOf(swap) == 0

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(bob) == 0
        assert coin.balanceOf(swap) == initial_amounts[i] - amounts[i]

    assert abs(pool_token.balanceOf(bob) - (n_coins * 10 ** 18 * base_amount - max_burn)) <= 1
    assert abs(pool_token.totalSupply() - (n_coins * 10 ** 18 * base_amount - max_burn)) <= 1


@pytest.mark.itercoins("idx")
def test_remove_some(
    bob,
    swap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    idx,
    initial_amounts,
    n_coins,
    base_amount,
):
    amounts = [i // 2 for i in initial_amounts]
    amounts[idx] = 0

    swap.remove_liquidity_imbalance(amounts, n_coins * 10 ** 18 * base_amount, True, {"from": bob})

    for i, coin in enumerate(underlying_coins):
        assert coin.balanceOf(bob) == amounts[i]
        assert coin.balanceOf(swap) == 0

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(bob) == 0
        assert coin.balanceOf(swap) == initial_amounts[i] - amounts[i]

    actual_balance = pool_token.balanceOf(bob)
    actual_total_supply = pool_token.totalSupply()
    ideal_balance = 10 ** 18 * base_amount * n_coins - 10 ** 18 * base_amount // 2 * (n_coins - 1)

    assert actual_balance == actual_total_supply
    assert ideal_balance * 0.99 < actual_balance < ideal_balance


@pytest.mark.itercoins("idx")
def test_remove_one(
    bob,
    swap,
    underlying_coins,
    wrapped_coins,
    pool_token,
    idx,
    initial_amounts,
    base_amount,
    n_coins,
):
    amounts = [0] * n_coins
    amounts[idx] = initial_amounts[idx] // 2

    swap.remove_liquidity_imbalance(amounts, n_coins * 10 ** 18 * base_amount, True, {"from": bob})

    for i, coin in enumerate(underlying_coins):
        assert coin.balanceOf(bob) == amounts[i]
        assert coin.balanceOf(swap) == 0

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(bob) == 0
        assert coin.balanceOf(swap) == initial_amounts[i] - amounts[i]

    actual_balance = pool_token.balanceOf(bob)
    actual_total_supply = pool_token.totalSupply()
    ideal_balance = 10 ** 18 * base_amount * n_coins - 10 ** 18 * base_amount // 2

    assert actual_balance == actual_total_supply
    assert ideal_balance * 0.99 < actual_balance < ideal_balance


@pytest.mark.parametrize("divisor", [1, 2, 10])
def test_exceed_max_burn(
    bob, swap, wrapped_coins, pool_token, divisor, initial_amounts, base_amount, n_coins
):
    amounts = [i // divisor for i in initial_amounts]
    max_burn = (n_coins * 10 ** 18 * base_amount) // divisor

    with brownie.reverts("Slippage screwed you"):
        swap.remove_liquidity_imbalance(amounts, max_burn - 1, True, {"from": bob})


def test_cannot_remove_zero(bob, swap, wrapped_coins, n_coins):
    with brownie.reverts():
        swap.remove_liquidity_imbalance([0] * n_coins, 0, True, {"from": bob})


def test_no_totalsupply(bob, swap, pool_token, n_coins):
    swap.remove_liquidity(pool_token.totalSupply(), [0] * n_coins, {"from": bob})
    with brownie.reverts():
        swap.remove_liquidity_imbalance([0] * n_coins, 0, True, {"from": bob})
