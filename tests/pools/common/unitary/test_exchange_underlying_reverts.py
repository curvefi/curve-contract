import brownie
import pytest

pytestmark = [pytest.mark.usefixtures("add_initial_liquidity", "approve_bob"), pytest.mark.lending]


@pytest.mark.itercoins("sending", "receiving")
def test_min_dy_too_high(bob, swap, underlying_coins, underlying_decimals, sending, receiving):
    amount = 10**underlying_decimals[sending]

    underlying_coins[sending]._mint_for_testing(bob, amount, {'from': bob})

    min_dy = swap.get_dy(sending, receiving, amount)
    with brownie.reverts("Exchange resulted in fewer coins than expected"):
        swap.exchange_underlying(sending, receiving, amount, min_dy+2, {'from': bob})


@pytest.mark.itercoins("sending", "receiving")
def test_insufficient_balance(bob, swap, underlying_coins, underlying_decimals, sending, receiving):
    amount = 10**underlying_decimals[sending]

    underlying_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
    with brownie.reverts():
        swap.exchange_underlying(sending, receiving, amount+1, 0, {'from': bob})


@pytest.mark.itercoins("idx")
def test_same_coin(bob, swap, idx):
    with brownie.reverts():
        swap.exchange_underlying(idx, idx, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [-1, -2**127])
def test_i_below_zero(bob, swap, idx):
    with brownie.reverts():
        swap.exchange_underlying(idx, 0, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [False, 2**127-1])
def test_i_above_n_coins(bob, swap, idx, n_coins):
    if idx is False:
        idx = n_coins
    with brownie.reverts():
        swap.exchange_underlying(idx, 0, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [-1, -2**127])
def test_j_below_zero(bob, swap, idx):
    with brownie.reverts():
        swap.exchange_underlying(0, idx, 0, 0, {'from': bob})


@pytest.mark.parametrize("idx", [False, 2**127-1])
def test_j_above_n_coins(bob, swap, idx, n_coins):
    if idx is False:
        idx = n_coins
    with brownie.reverts():
        swap.exchange_underlying(0, idx, 0, 0, {'from': bob})
