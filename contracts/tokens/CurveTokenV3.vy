# @version ^0.2.0
"""
@title Curve LP Token
@author Curve.Fi
@notice Base implementation for an LP token provided for
        supplying liquidity to `StableSwap`
@dev Follows the ERC-20 token standard as defined at
     https://eips.ethereum.org/EIPS/eip-20
"""

from vyper.interfaces import ERC20

implements: ERC20

interface Curve:
    def owner() -> address: view


event Transfer:
    _from: indexed(address)
    _to: indexed(address)
    _value: uint256

event Approval:
    _owner: indexed(address)
    _spender: indexed(address)
    _value: uint256


name: public(String[64])
symbol: public(String[32])

balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])
totalSupply: public(uint256)

minter: public(address)


@external
def __init__(_name: String[64], _symbol: String[32]):
    self.name = _name
    self.symbol = _symbol
    self.minter = msg.sender
    log Transfer(ZERO_ADDRESS, msg.sender, 0)


@view
@external
def decimals() -> uint256:
    return 18


@external
def transfer(_to : address, _value : uint256) -> bool:
    """
    @dev Transfer token for a specified address
    @param _to The address to transfer to.
    @param _value The amount to be transferred.
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    """
     @dev Transfer tokens from one address to another.
     @param _from address The address which you want to send tokens from
     @param _to address The address which you want to transfer to
     @param _value uint256 the amount of tokens to be transferred
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    if msg.sender != self.minter:  # minter is allowed to transfer anything
        _allowance: uint256 = self.allowance[_from][msg.sender]
        if _allowance != MAX_UINT256:
            # NOTE: vyper does not allow underflows
            # so the following subtraction would revert on insufficient allowance
            self.allowance[_from][msg.sender] = _allowance - _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    """
    @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
         Beware that changing an allowance with this method brings the risk that someone may use both the old
         and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
         race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
         https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    @param _spender The address which will spend the funds.
    @param _value The amount of tokens to be spent.
    """
    assert _value == 0 or self.allowance[msg.sender][_spender] == 0
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def mint(_to: address, _value: uint256) -> bool:
    """
    @dev Mint an amount of the token and assigns it to an account.
         This encapsulates the modification of balances such that the
         proper events are emitted.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    assert msg.sender == self.minter

    self.totalSupply += _value
    self.balanceOf[_to] += _value
    log Transfer(ZERO_ADDRESS, _to, _value)

    return True


@external
def burnFrom(_to: address, _value: uint256) -> bool:
    """
    @dev Burn an amount of the token from a given account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    assert msg.sender == self.minter

    self.totalSupply -= _value
    self.balanceOf[_to] -= _value
    log Transfer(_to, ZERO_ADDRESS, _value)

    return True


@external
def set_minter(_minter: address):
    assert msg.sender == self.minter
    self.minter = _minter


@external
def set_name(_name: String[64], _symbol: String[32]):
    assert Curve(self.minter).owner() == msg.sender
    self.name = _name
    self.symbol = _symbol
