# @version ^0.2.8
"""
@notice Mock rETH token
@dev This is for testing only, it is NOT safe for use
"""

from vyper.interfaces import ERC20

interface ERC20Mock:
    def decimals() -> uint256: view
    def _mint_for_testing(_target: address, _value: uint256) -> bool: nonpayable


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
decimals: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowances: HashMap[address, HashMap[address, uint256]]
total_supply: uint256

exchangeRateStored: public(uint256)

@external
def __init__(
    _name: String[64],
    _symbol: String[32],
    _decimals: uint256,
    _underlying_token: address
):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.exchangeRateStored = 10**18


@external
@view
def totalSupply() -> uint256:
    return self.total_supply


@external
@view
def allowance(_owner : address, _spender : address) -> uint256:
    return self.allowances[_owner][_spender]


@external
def transfer(_to : address, _value : uint256) -> bool:
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    self.allowances[_from][msg.sender] -= _value
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    self.allowances[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


# rETH-specific function
@view
@external
def getExchangeRate() -> uint256:
    rate: uint256 = self.exchangeRateStored
    return rate


@external
def set_exchange_rate(rate: uint256): 
    self.exchangeRateStored = rate


@external
def _mint_for_testing(_target: address, _value: uint256) -> bool:
    self.total_supply += _value
    self.balanceOf[_target] += _value
    log Transfer(ZERO_ADDRESS, _target, _value)

    return True
