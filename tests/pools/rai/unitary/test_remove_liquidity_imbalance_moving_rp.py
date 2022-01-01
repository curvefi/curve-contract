import brownie
import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity")
redemption_index = 0
lp_index = 1


@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
@pytest.mark.itercoins("zero_idx")
def test_remove_some_pool_token(alice, swap, wrapped_coins, pool_token, initial_amounts, n_coins, base_amount,
                                redemption_price_scale, zero_idx, redemption_price_snap):
    amounts = [i // 2 for i in initial_amounts]
    amounts[zero_idx] = 0
    initial_pool_token_total_supply = pool_token.totalSupply()
    # The redemption price is being doubled or halved, and half of either the redemption or base lp token is removed.
    # Each component of liquidity now accounts for either one or two thirds of the total.
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    swap.remove_liquidity_imbalance(amounts, n_coins * 10 ** 18 * base_amount, {"from": alice})
    for i, coin in enumerate(wrapped_coins):
        assert coin.balanceOf(alice) == amounts[i]
        assert coin.balanceOf(swap) == initial_amounts[i] - amounts[i]

    actual_balance = pool_token.balanceOf(alice)
    actual_total_supply = pool_token.totalSupply()
    assert actual_balance == actual_total_supply

    # Ensure a fair amount of LP tokens have been destroyed relative to the proportion of total liquidity value removed.
    # Approx used because there will be some small slippage.
    if (zero_idx == redemption_index) == (redemption_price_scale == 2):
        expected_pool_tokens_remaining_proportion = 5 / 6
    else:
        expected_pool_tokens_remaining_proportion = 2 / 3
    remaining_proportion = actual_total_supply / initial_pool_token_total_supply
    assert expected_pool_tokens_remaining_proportion == pytest.approx(remaining_proportion, rel=1e-3)


@pytest.mark.parametrize("divisor", [1, 2, 10])
@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
def test_exceed_max_burn(alice, swap, wrapped_coins, pool_token, divisor, initial_amounts, base_amount, n_coins,
                         redemption_price_scale, redemption_price_snap):
    amounts = [i // divisor for i in initial_amounts]
    max_burn = (n_coins * 10 ** 18 * base_amount) // divisor
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)

    # Ensure when withdrawing equal amounts of each coin the redemption price should not effect results compared to the
    # common version of this test.
    with brownie.reverts("Slippage screwed you"):
        swap.remove_liquidity_imbalance(amounts, max_burn - 1, {"from": alice})


@pytest.mark.parametrize("divisor", [2, 10])
@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
@pytest.mark.itercoins("zero_idx")
def test_exceed_max_burn_imbalanced(alice, swap, wrapped_coins, pool_token, divisor, initial_amounts, base_amount,
                                    n_coins, redemption_price_scale, redemption_price_snap, zero_idx):
    amounts = [i // divisor for i in initial_amounts]
    amounts[zero_idx] = 0
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    if (zero_idx == redemption_index) == (redemption_price_scale == 2):
        burn_scale = 2 / 3
    else:
        burn_scale = 4 / 3
    max_burn = (burn_scale * (n_coins - 1) * 10 ** 18 * base_amount) // divisor

    # Ensure the max burn moves with the redemption price to reflect the proportion of liquidity value removed
    with brownie.reverts("Slippage screwed you"):
        swap.remove_liquidity_imbalance(amounts, max_burn * 0.999, {"from": alice})
