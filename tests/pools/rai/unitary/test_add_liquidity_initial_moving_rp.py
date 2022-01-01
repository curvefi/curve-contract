import brownie
import pytest

pytestmark = pytest.mark.usefixtures("mint_alice", "approve_alice")


@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
@pytest.mark.parametrize("min_amount", [0, 2 * 10 ** 18])
def test_initial(alice, swap, wrapped_coins, pool_token, min_amount, wrapped_decimals, n_coins, initial_amounts,
                 redemption_price_scale, redemption_price_snap):
    amounts = [10 ** i for i in wrapped_decimals]
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    imbalance_scale = 0.5 + 0.5 * redemption_price_scale
    min_amount *= imbalance_scale * (1 - 1e-3)
    swap.add_liquidity(amounts, min_amount, {"from": alice, "value": 0})

    for coin, amount, initial in zip(wrapped_coins, amounts, initial_amounts):
        assert coin.balanceOf(alice) == initial - amount
        assert coin.balanceOf(swap) == amount

    std_amount = (n_coins * 10 ** 18)

    expected_balance = std_amount * imbalance_scale
    assert pytest.approx(pool_token.balanceOf(alice), rel=1e-3) == expected_balance
    assert pytest.approx(pool_token.totalSupply(), rel=1e-3) == expected_balance


@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
@pytest.mark.itercoins("idx")
def test_initial_liquidity_missing_coin(alice, swap, pool_token, idx, wrapped_decimals, redemption_price_scale,
                                        redemption_price_snap):
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    amounts = [10 ** i for i in wrapped_decimals]
    amounts[idx] = 0

    with brownie.reverts():
        swap.add_liquidity(amounts, 0, {"from": alice})
