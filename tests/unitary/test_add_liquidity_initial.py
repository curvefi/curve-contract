import brownie
import pytest

from tests.conftest import PRECISIONS


@pytest.fixture(scope="module", autouse=True)
def setup(alice, coins, swap):
    for coin in coins:
        coin._mint_for_testing(alice, 10**24, {'from': alice})
        coin.approve(swap, 10**24, {'from': alice})


@pytest.mark.parametrize("min_amount", [0, 2 * 10**18])
def test_add_initial_liquidity(alice, swap, coins, pool_token, min_amount):
    amounts = [10**i for i in PRECISIONS]
    swap.add_liquidity(amounts, min_amount, {'from': alice})

    for coin, amount in zip(coins, amounts):
        assert coin.balanceOf(alice) == 10**24 - amount
        assert coin.balanceOf(swap) == amount

    assert pool_token.balanceOf(alice) == 2 * 10**18
    assert pool_token.totalSupply() == 2 * 10**18


@pytest.mark.parametrize("idx", range(len(PRECISIONS)))
def test_initial_liquidity_missing_coin(alice, swap, coins, pool_token, idx):
    amounts = [10**i for i in PRECISIONS]
    amounts[idx] = 0
    with brownie.reverts("dev: initial deposit requires all coins"):
        swap.add_liquidity(amounts, 0, {'from': alice})
