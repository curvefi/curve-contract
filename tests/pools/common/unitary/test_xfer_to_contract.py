import pytest

from brownie import compile_source

ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


pytestmark = pytest.mark.usefixtures("add_initial_liquidity")


def test_unexpected_eth(swap, alice, bob, get_admin_balances, wrapped_coins):
    code = """
# @version 0.2.4

@payable
@external
def __init__(swap: address):
    selfdestruct(swap)
    """

    virtual_price = swap.get_virtual_price()

    compile_source(code, vyper_version="0.2.4").Vyper.deploy(swap, {'from': bob, 'value': 123456})

    assert swap.get_virtual_price() == virtual_price
    if ETH_ADDRESS in wrapped_coins:
        assert sum(get_admin_balances()) == 123456
    else:
        assert sum(get_admin_balances()) == 0


def test_unexpected_coin(swap, alice, bob, get_admin_balances, wrapped_coins):
    virtual_price = swap.get_virtual_price()

    wrapped_coins[-1]._mint_for_testing(swap, 123456, {'from': alice})

    assert swap.get_virtual_price() == virtual_price
    assert sum(get_admin_balances()) == 123456
