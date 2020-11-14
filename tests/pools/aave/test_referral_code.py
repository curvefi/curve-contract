import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob")


def test_only_owner(bob, swap):
    with brownie.reverts("dev: only owner"):
        swap.set_aave_referral(31337, {'from': bob})


@pytest.mark.parametrize("value", [2**16, 2**256-1])
def test_exceeds_bounds(alice, swap, value):
    with brownie.reverts("dev: uint16 overflow"):
        swap.set_aave_referral(value, {'from': alice})


def test_underlying_min_dy(alice, bob, swap, underlying_coins, aave_lending_pool):
    underlying_coins[0]._mint_for_testing(bob, 10**19, {'from': bob})

    swap.set_aave_referral(31337, {'from': alice})
    swap.exchange_underlying(0, 1, 10**18, 0, {'from': bob})

    assert aave_lending_pool.lastReferral() == 31337

    swap.set_aave_referral(42, {'from': alice})
    swap.exchange_underlying(0, 1, 10**18, 0, {'from': bob})

    assert aave_lending_pool.lastReferral() == 42
