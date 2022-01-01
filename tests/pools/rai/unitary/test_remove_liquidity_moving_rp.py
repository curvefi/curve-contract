import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


@pytest.mark.parametrize("redemption_price_scale", [0.5, 2])
def test_remove_liquidity(alice, swap, wrapped_coins, pool_token, initial_amounts, base_amount, n_coins,
                          redemption_price_scale, redemption_price_snap):
    # For clarity this is the state post setup. Alice has deposited 1MM each of redemption coin and lp token when the
    # redemption price was 1.
    assert pool_token.balanceOf(alice) == n_coins * 10 ** 18 * base_amount == pool_token.totalSupply()
    for coin, amount in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(swap) == 1000000 * 10**18

    # Now modify the redemption price and remove half the liquidity. The received tokens should be independent of the
    # redemption price, half the LP tokens should give half the underlying tokens.
    redemption_price_snap.setRedemptionPriceSnap(redemption_price_scale * 1e27)
    swap.remove_liquidity(
        n_coins * 10 ** 18 * base_amount / 2, [0, 0], {"from": alice}
    )

    for coin, amount in zip(wrapped_coins, initial_amounts):
        assert coin.balanceOf(alice) == amount / 2
        assert coin.balanceOf(swap) == amount / 2

    assert pool_token.balanceOf(alice) == n_coins * 10 ** 18 * base_amount / 2
    assert pool_token.totalSupply() == n_coins * 10 ** 18 * base_amount / 2
