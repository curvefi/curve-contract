import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


def test_redemption_price(chain, bob, swap, initial_amounts, n_coins, redemption_price_snap):
    redemption_price = redemption_price_snap.snappedRedemptionPrice()

    chain.sleep(86400)
    chain.mine()

    assert redemption_price == redemption_price_snap.snappedRedemptionPrice()

    redemption_price += 1e25
    redemption_price_snap.setRedemptionPriceSnap(redemption_price)

    chain.sleep(86400)
    chain.mine()

    assert redemption_price == redemption_price_snap.snappedRedemptionPrice()
