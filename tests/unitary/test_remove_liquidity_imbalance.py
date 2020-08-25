import brownie
import pytest

from tests.conftest import PRECISIONS

INITIAL_AMOUNTS = [10**(i+6) for i in PRECISIONS]


@pytest.fixture(scope="module", autouse=True)
def setup(alice, coins, swap):
    for coin, amount in zip(coins, INITIAL_AMOUNTS):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})

    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': alice})


@pytest.mark.parametrize("divisor", [2, 5, 10])
def test_remove_liquidity_balanced(alice, swap, coins, pool_token, divisor):
    amounts = [i // divisor for i in INITIAL_AMOUNTS]
    max_burn = (2 * 10**24) // divisor + 1
    swap.remove_liquidity_imbalance(amounts, max_burn, {'from': alice})

    for i, coin in enumerate(coins):
        assert coin.balanceOf(alice) == amounts[i]
        assert coin.balanceOf(swap) == INITIAL_AMOUNTS[i] - amounts[i]

    assert pool_token.balanceOf(alice) == (2 * 10**24) - max_burn
    assert pool_token.totalSupply() == (2 * 10**24) - max_burn


@pytest.mark.parametrize("idx", range(len(PRECISIONS)))
def test_remove_two_coins(alice, swap, coins, pool_token, idx):
    amounts = [i//2 for i in INITIAL_AMOUNTS]
    amounts[idx] = 0

    swap.remove_liquidity_imbalance(amounts, 2*10**24, {'from': alice})

    for i, coin in enumerate(coins):
        assert coin.balanceOf(alice) == amounts[i]
        assert coin.balanceOf(swap) == INITIAL_AMOUNTS[i] - amounts[i]

    actual_balance = pool_token.balanceOf(alice)
    actual_total_supply = pool_token.totalSupply()

    ideal_balance = 15 * 10**23
    assert actual_balance == actual_total_supply
    assert ideal_balance * 0.99 < actual_balance < ideal_balance


@pytest.mark.parametrize("idx", range(len(PRECISIONS)))
def test_remove_one_coin(alice, swap, coins, pool_token, idx):
    burn_amount = (2 * 10**24) // 2
    expected = swap.calc_withdraw_one_coin(burn_amount, idx)

    amounts = [0, 0]
    amounts[idx] = expected

    swap.remove_liquidity_imbalance(amounts, 2*10**24, {'from': alice})

    assert coins[idx].balanceOf(alice) == expected
    assert abs(pool_token.balanceOf(alice) - burn_amount) <= 10 ** 10


@pytest.mark.parametrize("divisor", [1, 2, 10])
def test_exceeds_max_burn(alice, swap, coins, pool_token, divisor):
    amounts = [i // divisor for i in INITIAL_AMOUNTS]
    max_burn = (2 * 10**24) // divisor

    with brownie.reverts("Slippage screwed you"):
        swap.remove_liquidity_imbalance(amounts, max_burn-1, {'from': alice})


def test_cannot_remove_zero(alice, swap):
    with brownie.reverts("dev: zero tokens burned"):
        swap.remove_liquidity_imbalance([0, 0], 0, {'from': alice})


def test_no_totalsupply(alice, swap, pool_token):
    swap.remove_liquidity(pool_token.totalSupply(), [0] * len(INITIAL_AMOUNTS), {'from': alice})
    with brownie.reverts("dev: zero total supply"):
        swap.remove_liquidity_imbalance([0, 0], 0, {'from': alice})
