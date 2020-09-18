import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "approve_bob")

ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


@pytest.mark.itercoins("sending", "receiving")
def test_insufficient_balance(bob, swap, wrapped_coins, sending, receiving, wrapped_decimals):
    amount = 10**wrapped_decimals[sending]
    if wrapped_coins[sending] == ETH_ADDRESS:
        value = amount
    else:
        wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
        value = 0

    with brownie.reverts():
        swap.exchange(sending, receiving, amount+1, 0, {'from': bob, 'value': value})


@pytest.mark.itercoins("sending", "receiving")
def test_min_dy_too_high(bob, swap, wrapped_coins, sending, receiving, wrapped_decimals):
    amount = 10**wrapped_decimals[sending]
    if wrapped_coins[sending] == ETH_ADDRESS:
        value = amount
    else:
        wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
        value = 0

    min_dy = swap.get_dy(sending, receiving, amount)
    with brownie.reverts():
        swap.exchange(sending, receiving, amount, min_dy+2, {'from': bob, 'value': value})


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
