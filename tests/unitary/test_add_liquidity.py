import brownie
import pytest

from tests.conftest import PRECISIONS

INITIAL_AMOUNTS = [10**(i+6) for i in PRECISIONS]


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, coins, swap):
    # mint (10**6 * precision) of each coin in the pool for alice and bob
    # alice provides all of her balances as the initial liquidity

    for coin, amount in zip(coins, INITIAL_AMOUNTS):
        for acct in (alice, bob):
            coin._mint_for_testing(acct, amount, {'from': acct})
            coin.approve(swap, 2**256-1, {'from': acct})

    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': alice})


def test_add_liquidity(bob, swap, coins, pool_token):
    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': bob})

    for coin, amount in zip(coins, INITIAL_AMOUNTS):
        assert coin.balanceOf(bob) == 0
        assert coin.balanceOf(swap) == amount * 2

    assert pool_token.balanceOf(bob) == 2 * 10**24
    assert pool_token.totalSupply() == 4 * 10**24


def test_add_liquidity_with_slippage(bob, swap, coins, pool_token):
    amounts = [10**i for i in PRECISIONS]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    swap.add_liquidity(amounts, 0, {'from': bob})

    assert 0.999 < pool_token.balanceOf(bob) / (2 * 10**18) < 1


@pytest.mark.parametrize("idx", range((len(PRECISIONS))))
def test_add_liquidity_one_coin(bob, swap, coins, pool_token, idx):
    amounts = [0, 0]
    amounts[idx] = INITIAL_AMOUNTS[idx]
    swap.add_liquidity(amounts, 0, {'from': bob})

    for i, coin in enumerate(coins):
        assert coin.balanceOf(bob) == INITIAL_AMOUNTS[i] - amounts[i]
        assert coin.balanceOf(swap) == INITIAL_AMOUNTS[i] + amounts[i]

    assert 0.999 < pool_token.balanceOf(bob) / 10**24 < 1


def test_insufficient_balance(charlie, swap, coins, pool_token):
    amounts = [(10**i) for i in PRECISIONS]
    with brownie.reverts("dev: failed transfer"):
        swap.add_liquidity(amounts, 0, {'from': charlie})


@pytest.mark.parametrize("min_amount", [3 * 10**18 + 1, 2**256-1])
def test_min_amount_too_high(alice, swap, coins, pool_token, min_amount):
    amounts = [10**i for i in PRECISIONS]
    with brownie.reverts("Slippage screwed you"):
        swap.add_liquidity(amounts, min_amount, {'from': alice})


def test_min_amount_with_slippage(bob, swap, coins, pool_token):
    amounts = [10**i for i in PRECISIONS]
    amounts[0] = int(amounts[0] * 0.99)
    amounts[1] = int(amounts[1] * 1.01)
    with brownie.reverts("Slippage screwed you"):
        swap.add_liquidity(amounts, 3 * 10**18, {'from': bob})
