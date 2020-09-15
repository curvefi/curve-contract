from itertools import combinations_with_replacement

import pytest
from pytest import approx


pytestmark = pytest.mark.lending()


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, underlying_coins, wrapped_coins, swap, initial_amounts):
    # mint (10**6 * precision) of each coin in the pool
    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        underlying._mint_for_testing(alice, amount, {'from': alice})
        underlying.approve(wrapped, 2**256-1, {'from': alice})
        wrapped.approve(swap, 2**256-1, {'from': alice})
        if hasattr(wrapped, "mint"):
            wrapped.mint(amount, {'from': alice})

    for coin in underlying_coins:
        coin.approve(swap, 2**256-1, {'from': bob})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})


@pytest.mark.itercoins("sending", "receiving")
@pytest.mark.parametrize("fee,admin_fee", combinations_with_replacement([0, 0.04, 0.1337, 0.5], 2))
def test_exchange_underlying(
    bob,
    swap,
    underlying_coins,
    sending,
    receiving,
    fee,
    admin_fee,
    underlying_decimals,
    set_fees,
    get_admin_balances,
):
    if fee or admin_fee:
        set_fees(10**10 * fee, 10**10 * admin_fee)

    amount = 10**underlying_decimals[sending]
    underlying_coins[sending]._mint_for_testing(bob, amount, {'from': bob})
    swap.exchange_underlying(sending, receiving, amount, 0, {'from': bob})

    assert underlying_coins[sending].balanceOf(bob) == 0

    received = underlying_coins[receiving].balanceOf(bob)
    assert 0.9999-fee < received / 10**underlying_decimals[receiving] < 1-fee

    expected_admin_fee = 10**underlying_decimals[receiving] * fee * admin_fee
    admin_fees = get_admin_balances()

    if expected_admin_fee:
        assert expected_admin_fee / admin_fees[receiving] == approx(1, rel=1e-3)
    else:
        assert admin_fees[receiving] <= 1


@pytest.mark.itercoins("sending", "receiving")
def test_min_dy_underlying(bob, swap, underlying_coins, sending, receiving, underlying_decimals):
    amount = 10**underlying_decimals[sending]
    underlying_coins[sending]._mint_for_testing(bob, amount, {'from': bob})

    min_dy = swap.get_dy(sending, receiving, amount)
    swap.exchange_underlying(sending, receiving, amount, min_dy, {'from': bob})

    assert abs(underlying_coins[receiving].balanceOf(bob) - min_dy) <= 1
