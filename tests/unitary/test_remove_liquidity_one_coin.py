import brownie
import pytest

from tests.conftest import PRECISIONS

INITIAL_AMOUNTS = [10**(i+6) for i in PRECISIONS]


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bank, coins, swap):
    for coin, amount in zip(coins[:-1], INITIAL_AMOUNTS[:-1]):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})
    coins[-1].transfer(
            bank, coins[-1].balanceOf(alice) - INITIAL_AMOUNTS[-1],
            {'from': alice})
    coins[-1].approve(swap, 2**256-1, {'from': alice})

    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': alice})


@pytest.mark.parametrize("idx", range(len(PRECISIONS)))
@pytest.mark.parametrize("divisor", [1, 5, 42])
def test_remove_one_coin(alice, swap, coins, pool_token, idx, divisor):
    amount = pool_token.balanceOf(alice) // divisor

    expected = swap.calc_withdraw_one_coin(amount, idx)
    swap.remove_liquidity_one_coin(amount, idx, 0, {'from': alice})

    assert coins[idx].balanceOf(alice) == expected
    assert pool_token.balanceOf(alice) == 2 * 10**24 - amount


@pytest.mark.parametrize("idx", range(len(PRECISIONS)))
def test_below_min_amount(alice, swap, coins, pool_token, idx):
    amount = pool_token.balanceOf(alice)

    expected = swap.calc_withdraw_one_coin(amount, idx)
    with brownie.reverts("Not enough coins removed"):
        swap.remove_liquidity_one_coin(amount, idx, expected+1, {'from': alice})


@pytest.mark.parametrize("idx", range(len(PRECISIONS)))
def test_amount_exceeds_balance(bob, swap, coins, pool_token, idx):
    with brownie.reverts("dev: insufficient funds"):
        swap.remove_liquidity_one_coin(1, idx, 0, {'from': bob})


def test_below_zero(alice, swap):
    with brownie.reverts("dev: i below zero"):
        swap.remove_liquidity_one_coin(1, -1, 0, {'from': alice})


def test_above_ncoins(alice, swap):
    with brownie.reverts("dev: i above N_COINS"):
        swap.remove_liquidity_one_coin(1, 3, 0, {'from': alice})
