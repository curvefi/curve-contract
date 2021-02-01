import pytest
from brownie import compile_source

pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


code = """
# @version 0.2.8

@payable
@external
def __init__(swap: address):
    selfdestruct(swap)
    """


def test_virtual_price_increases_with_balances(bob, swap, wrapped_coins, initial_amounts):
    amount = initial_amounts[0]
    virtual_price = swap.get_virtual_price()

    compile_source(code, vyper_version="0.2.8").Vyper.deploy(swap, {"from": bob, "value": amount})
    wrapped_coins[1]._mint_for_testing(swap, amount, {"from": bob})

    assert swap.get_virtual_price() // 2 == virtual_price


def test_admin_balances_do_not_change(bob, swap, wrapped_coins, initial_amounts, n_coins):
    amount = initial_amounts[0]

    for i in range(n_coins):
        assert swap.admin_balances(i) == 0

    compile_source(code, vyper_version="0.2.8").Vyper.deploy(swap, {"from": bob, "value": amount})
    wrapped_coins[1]._mint_for_testing(swap, amount, {"from": bob})

    for i in range(n_coins):
        assert swap.admin_balances(i) == 0
