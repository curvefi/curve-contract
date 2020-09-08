from itertools import combinations_with_replacement

import pytest
from pytest import approx


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, wrapped_coins, swap, initial_amounts):
    for coin, amount in zip(wrapped_coins, initial_amounts):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': bob})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


@pytest.mark.itercoins("sending", "receiving")
@pytest.mark.parametrize("fee,admin_fee", combinations_with_replacement([0, 0.04, 0.1337, 0.5], 2))
def test_exchange(
    bob,
    swap,
    wrapped_coins,
    sending,
    receiving,
    fee,
    admin_fee,
    wrapped_decimals,
    set_fees,
    get_admin_balances,
):
    if fee or admin_fee:
        set_fees(10**10 * fee, 10**10 * admin_fee)

    amount = 10**wrapped_decimals[sending]
    wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
    swap.exchange(sending, receiving, amount, 0, {'from': bob})

    assert wrapped_coins[sending].balanceOf(bob) == 0

    received = wrapped_coins[receiving].balanceOf(bob)
    assert 0.9999-fee < received / 10**wrapped_decimals[receiving] < 1-fee

    expected_admin_fee = 10**wrapped_decimals[receiving] * fee * admin_fee
    admin_fees = get_admin_balances()

    if expected_admin_fee:
        assert expected_admin_fee / admin_fees[receiving] == approx(1, rel=1e-3)
    else:
        assert admin_fees[receiving] <= 1


@pytest.mark.itercoins("sending", "receiving")
def test_min_dy(bob, swap, wrapped_coins, sending, receiving, wrapped_decimals):
    amount = 10**wrapped_decimals[sending]
    wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})

    min_dy = swap.get_dy(sending, receiving, amount)
    swap.exchange(sending, receiving, amount, min_dy, {'from': bob})

    assert abs(wrapped_coins[receiving].balanceOf(bob) - min_dy) <= 1
