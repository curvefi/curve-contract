import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(alice, wrapped_coins, swap, initial_amounts):
    for coin, amount in zip(wrapped_coins, initial_amounts):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


@pytest.mark.parametrize("divisor", [2, 5, 10])
def test_remove_balanced(alice, swap, wrapped_coins, pool_token, divisor, initial_amounts, n_coins):
    amounts = [i // divisor for i in initial_amounts]
    max_burn = (n_coins * 10**24) // divisor
    swap.remove_liquidity_imbalance(amounts, max_burn + 1, {'from': alice})

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(alice) == amounts[i]
        assert coin.balanceOf(swap) == initial_amounts[i] - amounts[i]

    assert abs(pool_token.balanceOf(alice) - (n_coins * 10**24 - max_burn)) <= 1
    assert abs(pool_token.totalSupply() - (n_coins * 10**24 - max_burn)) <= 1


@pytest.mark.itercoins("idx")
def test_remove_some(alice, swap, wrapped_coins, pool_token, idx, initial_amounts, n_coins):
    amounts = [i//2 for i in initial_amounts]
    amounts[idx] = 0

    swap.remove_liquidity_imbalance(amounts, n_coins*10**24, {'from': alice})

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(alice) == amounts[i]
        assert coin.balanceOf(swap) == initial_amounts[i] - amounts[i]

    actual_balance = pool_token.balanceOf(alice)
    actual_total_supply = pool_token.totalSupply()
    ideal_balance = 10 ** 24 * n_coins - 10 ** 24 // 2 * (n_coins-1)

    assert actual_balance == actual_total_supply
    assert ideal_balance * 0.99 < actual_balance < ideal_balance


@pytest.mark.itercoins("idx")
def test_remove_one(alice, swap, wrapped_coins, pool_token, idx, initial_amounts, n_coins):
    amounts = [0] * n_coins
    amounts[idx] = initial_amounts[idx] // 2

    swap.remove_liquidity_imbalance(amounts, n_coins*10**24, {'from': alice})

    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(alice) == amounts[i]
        assert coin.balanceOf(swap) == initial_amounts[i] - amounts[i]

    actual_balance = pool_token.balanceOf(alice)
    actual_total_supply = pool_token.totalSupply()
    ideal_balance = 10 ** 24 * n_coins - 10**24 // 2

    assert actual_balance == actual_total_supply
    assert ideal_balance * 0.99 < actual_balance < ideal_balance


@pytest.mark.parametrize("divisor", [1, 2, 10])
def test_exceed_max_burn(alice, swap, wrapped_coins, pool_token, divisor, initial_amounts, n_coins):
    amounts = [i // divisor for i in initial_amounts]
    max_burn = (n_coins * 10**24) // divisor

    with brownie.reverts("Slippage screwed you"):
        swap.remove_liquidity_imbalance(amounts, max_burn-1, {'from': alice})


def test_cannot_remove_zero(alice, swap, wrapped_coins, n_coins):
    with brownie.reverts():
        swap.remove_liquidity_imbalance([0] * n_coins, 0, {'from': alice})


def test_no_totalsupply(alice, swap, pool_token, n_coins):
    swap.remove_liquidity(pool_token.totalSupply(), [0] * n_coins, {'from': alice})
    with brownie.reverts():
        swap.remove_liquidity_imbalance([0] * n_coins, 0, {'from': alice})
