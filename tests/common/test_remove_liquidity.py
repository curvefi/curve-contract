import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(alice, wrapped_coins, swap, initial_amounts):
    for coin, amount in zip(wrapped_coins, initial_amounts):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


@pytest.mark.parametrize("min_amount", (0, 1))
def test_remove_liquidity(alice, swap, wrapped_coins, pool_token, min_amount, initial_amounts, n_coins):
    swap.remove_liquidity(n_coins * 10**24, [i * min_amount for i in initial_amounts], {'from': alice})

    for coin, amount in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(alice) == amount
        assert coin.balanceOf(swap) == 0

    assert pool_token.balanceOf(alice) == 0
    assert pool_token.totalSupply() == 0


def test_remove_partial(alice, swap, wrapped_coins, pool_token, initial_amounts, n_coins):
    withdraw_amount = sum(initial_amounts) // 2
    swap.remove_liquidity(withdraw_amount, [0] * n_coins, {'from': alice})

    for coin, amount in zip(wrapped_coins, initial_amounts):
        pool_balance = coin.balanceOf(swap)
        alice_balance = coin.balanceOf(alice)
        assert alice_balance + pool_balance == amount

    assert pool_token.balanceOf(alice) == n_coins * 10**24 - withdraw_amount
    assert pool_token.totalSupply() == n_coins * 10**24 - withdraw_amount


@pytest.mark.itercoins("idx")
def test_below_min_amount(alice, swap, initial_amounts, n_coins, idx):
    min_amount = initial_amounts.copy()
    min_amount[idx] += 1

    with brownie.reverts():
        swap.remove_liquidity(n_coins * 10**24, min_amount, {'from': alice})


def test_amount_exceeds_balance(alice, swap, n_coins):
    with brownie.reverts():
        swap.remove_liquidity(n_coins * 10**24 + 1, [0] * n_coins, {'from': alice})
