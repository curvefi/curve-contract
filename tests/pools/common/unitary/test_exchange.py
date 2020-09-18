from itertools import combinations_with_replacement

import pytest
from pytest import approx

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "approve_bob")

ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


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
    if wrapped_coins[sending] == ETH_ADDRESS:
        value = amount
    else:
        wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
        value = 0

    swap.exchange(sending, receiving, amount, 0, {'from': bob, 'value': value})

    if wrapped_coins[sending] == ETH_ADDRESS:
        assert bob.balance() + amount == "1000000 ether"
    else:
        assert wrapped_coins[sending].balanceOf(bob) == 0

    if wrapped_coins[receiving] == ETH_ADDRESS:
        received = bob.balance() - "1000000 ether"
    else:
        received = wrapped_coins[receiving].balanceOf(bob)
    assert 1 - max(1e-4, 1/received) - fee < received / 10**wrapped_decimals[receiving] < 1-fee

    expected_admin_fee = 10**wrapped_decimals[receiving] * fee * admin_fee
    admin_fees = get_admin_balances()

    if expected_admin_fee >= 1:
        assert expected_admin_fee / admin_fees[receiving] == approx(1, rel=max(1e-3, 1/(expected_admin_fee-1.1)))
    else:
        assert admin_fees[receiving] <= 1


@pytest.mark.itercoins("sending", "receiving")
def test_min_dy(bob, swap, wrapped_coins, sending, receiving, wrapped_decimals):
    amount = 10**wrapped_decimals[sending]
    if wrapped_coins[sending] == ETH_ADDRESS:
        value = amount
    else:
        wrapped_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
        value = 0

    min_dy = swap.get_dy(sending, receiving, amount)
    swap.exchange(sending, receiving, amount, min_dy-1, {'from': bob, 'value': value})

    if wrapped_coins[receiving] == ETH_ADDRESS:
        received = bob.balance() - "1000000 ether"
    else:
        received = wrapped_coins[receiving].balanceOf(bob)

    assert abs(received - min_dy) <= 1
