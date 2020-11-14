import pytest

pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob")


def test_virtual_price_increases_with_balances(alice, swap, wrapped_coins, initial_amounts):
    virtual_price = swap.get_virtual_price()

    for i, coin in enumerate(wrapped_coins):
        coin._mint_for_testing(swap, initial_amounts[i], {'from': alice})

    assert swap.get_virtual_price() // 2 == virtual_price


def test_admin_balances_do_not_change(alice, swap, wrapped_coins, initial_amounts, n_coins):
    for i in range(n_coins):
        assert swap.admin_balances(i) == 0

    for i, coin in enumerate(wrapped_coins):
        coin._mint_for_testing(swap, initial_amounts[i], {'from': alice})

    for i in range(n_coins):
        assert swap.admin_balances(i) == 0
