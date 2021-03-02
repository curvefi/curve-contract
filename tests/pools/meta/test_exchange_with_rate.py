import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "approve_bob")


@pytest.mark.skip_pool("bbtc", "tbtc", "obtc", "pbtc", "template-meta")
@pytest.mark.itercoins("sending", "receiving")
def test_exchange_with_virtual_price(
    alice,
    bob,
    swap,
    underlying_coins,
    sending,
    receiving,
    underlying_decimals,
    base_amount,
    n_coins,
    base_swap,
    is_metapool,
    pool_token,
):
    amount = (base_amount // 100) * 10 ** underlying_decimals[sending]
    expected_dy = swap.get_dy_underlying(sending, receiving, amount)

    vp = base_swap.get_virtual_price.call()
    underlying_coins[n_coins - 1]._mint_for_testing(
        base_swap, amount * 1e9
    )  # mint sufficient amount

    base_swap.donate_admin_fees()  # dev: increase base pool virtual price
    assert vp < base_swap.get_virtual_price.call()

    underlying_coins[sending]._mint_for_testing(bob, amount, {"from": bob})

    tx = swap.exchange_underlying(sending, receiving, amount, 0, {"from": bob})
    dy = tx.events["TokenExchangeUnderlying"]["tokens_bought"]

    if sending < n_coins - 1:
        # dx is meta token
        assert dy > expected_dy
    else:
        # dx is base token
        assert dy < expected_dy
