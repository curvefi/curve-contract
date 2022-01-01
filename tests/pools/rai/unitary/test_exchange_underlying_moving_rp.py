from itertools import permutations

import pytest
from pytest import approx

pytestmark = [pytest.mark.usefixtures("add_initial_liquidity", "approve_bob"), pytest.mark.lending]
redemption_index = 0


@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
@pytest.mark.itercoins("sending", "receiving", underlying=True)
@pytest.mark.parametrize("fee,admin_fee", set(permutations([0, 0], 2)))
def test_amounts(
    bob,
    swap,
    underlying_coins,
    sending,
    receiving,
    fee,
    admin_fee,
    underlying_decimals,
    set_fees,
    n_coins,
    is_metapool,
    redemption_price_scale,
    redemption_price_snap,
):
    if fee or admin_fee:
        set_fees(10 ** 10 * fee, 10 ** 10 * admin_fee)

    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    amount = 10 ** underlying_decimals[sending]
    underlying_coins[sending]._mint_for_testing(bob, amount, {"from": bob})
    swap.exchange_underlying(sending, receiving, amount, 0, {"from": bob})

    assert underlying_coins[sending].balanceOf(bob) == 0

    received = underlying_coins[receiving].balanceOf(bob)
    if receiving == redemption_index:
        expected = 1 / redemption_price_scale
    elif sending == redemption_index:
        expected = redemption_price_scale
    else:
        expected = 1
    assert approx(expected, rel=1e-2) == received / 10 ** underlying_decimals[receiving]


@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
@pytest.mark.itercoins("sending", "receiving", underlying=True)
def test_min_dy_underlying(bob, swap, underlying_coins, sending, receiving, underlying_decimals, redemption_price_scale,
                           redemption_price_snap):
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    amount = 100 * 10 ** underlying_decimals[sending]
    underlying_coins[sending]._mint_for_testing(bob, amount, {"from": bob})
    min_dy = swap.get_dy_underlying(sending, receiving, amount)
    swap.exchange_underlying(sending, receiving, amount, min_dy - 1, {"from": bob})
    assert abs(underlying_coins[receiving].balanceOf(bob) - min_dy) <= 1
