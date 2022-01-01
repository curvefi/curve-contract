import pytest
from pytest import approx

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "approve_bob")
redemption_index = 0
lp_index = 1


@pytest.mark.parametrize("redemption_price_scale", [0.75, 1.0, 1.25])
def test_exchange_results_with_moving_redemption_price(
    bob,
    swap,
    wrapped_coins,
    base_amount,
    get_admin_balances,
    redemption_price_scale,
    redemption_price_snap,
):
    redemption_coin = wrapped_coins[redemption_index]
    lp_coin = wrapped_coins[lp_index]
    precision = 10 ** 18
    trade_quantity = 10 * precision
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    redemption_coin._mint_for_testing(bob, trade_quantity, {"from": bob})
    swap.exchange(redemption_index, lp_index, trade_quantity, 0, {"from": bob, "value": 0})
    assert redemption_coin.balanceOf(bob) == 0
    received = lp_coin.balanceOf(bob)
    assert trade_quantity * redemption_price_scale == approx(received, rel=1e-3)
    swap.exchange(lp_index, redemption_index, received, 0, {"from": bob, "value": 0})
    assert approx(redemption_coin.balanceOf(bob)) == trade_quantity
    assert lp_coin.balanceOf(bob) == 0
