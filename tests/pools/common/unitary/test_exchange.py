from itertools import combinations_with_replacement

import pytest
from pytest import approx

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "approve_bob")

ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


@pytest.mark.itercoins("sending", "receiving")
@pytest.mark.parametrize("fee,admin_fee", combinations_with_replacement([0, 0.04, 0.1337, 0.5], 2))
def test_exchange(
    bob,
    swap,
    wrapped_coins,
    sending,
    receiving,
    fee,
    admin_fee,
    wrapped_decimals,
    base_amount,
    set_fees,
    get_admin_balances,
):
    if fee or admin_fee:
        set_fees(10 ** 10 * fee, 10 ** 10 * admin_fee)

    amount = 10 ** wrapped_decimals[sending]
    if wrapped_coins[sending] == ETH_ADDRESS:
        value = amount
    else:
        wrapped_coins[sending]._mint_for_testing(bob, amount, {"from": bob})
        value = 0

    swap.exchange(sending, receiving, amount, 0, {"from": bob, "value": value})

    if wrapped_coins[sending] == ETH_ADDRESS:
        assert bob.balance() + amount == 10 ** 18 * base_amount
    else:
        assert wrapped_coins[sending].balanceOf(bob) == 0

    if wrapped_coins[receiving] == ETH_ADDRESS:
        received = bob.balance() - 10 ** 18 * base_amount
    else:
        received = wrapped_coins[receiving].balanceOf(bob)
    assert (
        1 - max(1e-4, 1 / received) - fee < received / 10 ** wrapped_decimals[receiving] < 1 - fee
    )

    expected_admin_fee = 10 ** wrapped_decimals[receiving] * fee * admin_fee
    admin_fees = get_admin_balances()

    if expected_admin_fee >= 1:
        assert expected_admin_fee / admin_fees[receiving] == approx(
            1, rel=max(1e-3, 1 / (expected_admin_fee - 1.1))
        )
    else:
        assert admin_fees[receiving] <= 1


@pytest.mark.itercoins("sending", "receiving")
def test_min_dy(bob, swap, wrapped_coins, sending, receiving, wrapped_decimals, base_amount):
    amount = 10 ** wrapped_decimals[sending]
    if wrapped_coins[sending] == ETH_ADDRESS:
        value = amount
    else:
        wrapped_coins[sending]._mint_for_testing(bob, amount, {"from": bob})
        value = 0

    min_dy = swap.get_dy(sending, receiving, amount)
    swap.exchange(sending, receiving, amount, min_dy - 1, {"from": bob, "value": value})

    if wrapped_coins[receiving] == ETH_ADDRESS:
        received = bob.balance() - 10 ** 18 * base_amount
    else:
        received = wrapped_coins[receiving].balanceOf(bob)

    assert abs(received - min_dy) <= 1


@pytest.mark.itercoins("sending", "receiving")
def test_exchange_with_virtual_price(
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
    if not is_metapool:
        return

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
