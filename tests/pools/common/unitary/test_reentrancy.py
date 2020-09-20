import brownie
import pytest

from brownie import compile_source, history

pytestmark = [
    pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob"),
    pytest.mark.target_pool("eth")
]


def test_exchange(swap, alice, wrapped_coins):
    code = """
# @version ^0.2.0

from vyper.interfaces import ERC20

interface StableSwap:
    def exchange(i: int128, j: int128, dx: uint256, min_dy: uint256): payable

event Callback:
    pass

called: bool

@payable
@external
def __default__():
    if not self.called:
        log Callback()
        self.called = True
        StableSwap(msg.sender).exchange(1, 0, 10**18, 0)


@external
def exchange(_coin: address, _swap: address):
    ERC20(_coin).approve(_swap, MAX_UINT256)
    StableSwap(_swap).exchange(1, 0, 10**18, 0)
    """

    contract = compile_source(code, vyper_version="0.2.4").Vyper.deploy({'from': alice})
    coin = wrapped_coins[1]
    coin._mint_for_testing(contract, 2 * 10**18, {'from': alice})

    with brownie.reverts():
        contract.exchange(coin, swap, {'from': alice})

    assert "Callback" in history[-1].events


def test_remove_liquidity(swap, alice, n_coins, pool_token):
    code = f"""
# @version ^0.2.0

interface StableSwap:
    def remove_liquidity(_amount: uint256, _min_amounts: uint256[{n_coins}]): nonpayable

event Callback:
    pass

called: bool

@payable
@external
def __default__():
    if not self.called:
        log Callback()
        self.called = True
        StableSwap(msg.sender).remove_liquidity(10**18, [{'0,' * n_coins}])


@external
def remove_liquidity(_swap: address):
    StableSwap(_swap).remove_liquidity(10**18, [{'0,' * n_coins}])
    """

    contract = compile_source(code, vyper_version="0.2.4").Vyper.deploy({'from': alice})
    pool_token.transfer(contract, pool_token.balanceOf(alice), {'from': alice})

    with brownie.reverts():
        contract.remove_liquidity(swap, {'from': alice})

    assert "Callback" in history[-1].events


def test_remove_liquidity_imbalance(swap, alice, n_coins, pool_token):
    code = f"""
# @version ^0.2.0

interface StableSwap:
    def remove_liquidity_imbalance(amounts: uint256[{n_coins}], max_burn: uint256): nonpayable

event Callback:
    pass

called: bool

@payable
@external
def __default__():
    if not self.called:
        log Callback()
        self.called = True
        StableSwap(msg.sender).remove_liquidity_imbalance([{'10**18, ' * n_coins}], MAX_UINT256)


@external
def remove_liquidity_imbalance(_swap: address):
    StableSwap(_swap).remove_liquidity_imbalance([{'10**18, ' * n_coins}], MAX_UINT256)
    """

    contract = compile_source(code, vyper_version="0.2.4").Vyper.deploy({'from': alice})
    pool_token.transfer(contract, pool_token.balanceOf(alice), {'from': alice})

    with brownie.reverts():
        contract.remove_liquidity_imbalance(swap, {'from': alice})

    assert "Callback" in history[-1].events


def test_remove_liquidity_one_coin(swap, alice, pool_token):
    code = f"""
# @version ^0.2.0

interface StableSwap:
    def remove_liquidity_one_coin(amount: uint256, i: int128, min_amount: uint256): nonpayable

event Callback:
    pass

called: bool

@payable
@external
def __default__():
    if not self.called:
        log Callback()
        self.called = True
        StableSwap(msg.sender).remove_liquidity_one_coin(10**18, 0, 0)


@external
def remove_liquidity_one_coin(_swap: address):
    StableSwap(_swap).remove_liquidity_one_coin(10**18, 0, 0)
    """

    contract = compile_source(code, vyper_version="0.2.4").Vyper.deploy({'from': alice})
    pool_token.transfer(contract, pool_token.balanceOf(alice), {'from': alice})

    with brownie.reverts():
        contract.remove_liquidity_one_coin(swap, {'from': alice})

    assert "Callback" in history[-1].events
