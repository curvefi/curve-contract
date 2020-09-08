import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, wrapped_coins, swap, initial_amounts):
    for coin, amount in zip(wrapped_coins, initial_amounts):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': bob})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


@pytest.mark.itercoins("sending", "receiving")
def test_insufficient_balance(bob, swap, wrapped_coins, sending, receiving, wrapped_decimals):
    amount = 10**wrapped_decimals[sending]
    wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})

    with brownie.reverts():
        swap.exchange(sending, receiving, amount+1, 0, {'from': bob})


@pytest.mark.itercoins("sending", "receiving")
def test_min_dy_too_high(bob, swap, wrapped_coins, sending, receiving, wrapped_decimals):
    amount = 10**wrapped_decimals[sending]
    wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})

    min_dy = swap.get_dy(sending, receiving, amount)
    with brownie.reverts():
        swap.exchange(sending, receiving, amount, min_dy+2, {'from': bob})


@pytest.mark.itercoins("idx")
def test_same_coin(bob, swap, idx):
    with brownie.reverts():
        swap.exchange(idx, idx, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [-1, -2**127])
def test_i_below_zero(bob, swap, idx):
    with brownie.reverts():
        swap.exchange(idx, 0, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [9, 2**127-1])
def test_i_above_n_coins(bob, swap, idx):
    with brownie.reverts():
        swap.exchange(idx, 0, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [-1, -2**127])
def test_j_below_zero(bob, swap, idx):
    with brownie.reverts():
        swap.exchange(0, idx, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [9, 2**127-1])
def test_j_above_n_coins(bob, swap, idx):
    with brownie.reverts():
        swap.exchange(0, idx, 0, 0, {'from': bob})
