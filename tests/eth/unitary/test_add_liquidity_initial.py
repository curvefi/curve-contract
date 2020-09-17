import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(alice, wrapped_coins, swap):
    for coin in wrapped_coins:
        coin._mint_for_testing(alice, 10**24, {'from': alice})
        coin.approve(swap, 10**24, {'from': alice})


@pytest.mark.parametrize("min_amount", [0, 2 * 10**18])
def test_initial(alice, swap, wrapped_coins, pool_token, min_amount, wrapped_decimals, n_coins):
    amounts = [10**i for i in wrapped_decimals]
    swap.add_liquidity(amounts, min_amount, {'from': alice})

    for coin, amount in zip(wrapped_coins, amounts):
        assert coin.balanceOf(alice) == 10**24 - amount
        assert coin.balanceOf(swap) == amount

    assert pool_token.balanceOf(alice) == n_coins * 10**18
    assert pool_token.totalSupply() == n_coins * 10**18


@pytest.mark.itercoins("idx")
def test_initial_liquidity_missing_coin(alice, swap, pool_token, idx, wrapped_decimals):
    amounts = [10**i for i in wrapped_decimals]
    amounts[idx] = 0

    with brownie.reverts():
        swap.add_liquidity(amounts, 0, {'from': alice})
