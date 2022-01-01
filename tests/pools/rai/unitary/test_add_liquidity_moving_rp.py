import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob")
redemption_index = 0
lp_index = 1


@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
@pytest.mark.itercoins("zero_idx")
def test_add_liquidity(bob, swap, wrapped_coins, pool_token, initial_amounts, base_amount, n_coins, zero_idx,
                       redemption_price_scale, redemption_price_snap):
    initial_pool_token_total_supply = pool_token.totalSupply()
    new_to_initial_deposit_scale = 1e-21
    deposit_amounts = [initial_amounts[i] * new_to_initial_deposit_scale for i in range(n_coins)]
    deposit_amounts[zero_idx] = 0

    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    swap.add_liquidity(deposit_amounts, 0, {"from": bob, "value": 0})
    pool_tokens_earned = pool_token.balanceOf(bob)

    tvl_prop = 0.5 + 0.5 * redemption_price_scale  # half of liquidity val has been scaled by redemption price
    deposited_coin_val = 1
    if zero_idx == lp_index:
        deposited_coin_val = redemption_price_scale
    expected = initial_pool_token_total_supply * new_to_initial_deposit_scale / 2 * deposited_coin_val / tvl_prop
    assert pytest.approx(pool_tokens_earned, rel=1e-3) == expected
