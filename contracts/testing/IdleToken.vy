# @version ^0.2.0

"""
@notice Mock Idle Token
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

underlying_token: address
tokenPrice: public(uint256)
withdrawal_fee: uint256


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
    self.underlying_token = _underlying_token
    self.tokenPrice = 10**ERC20Mock(_underlying_token).decimals()


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


# yERC20-specific functions
@external
def mintIdleToken(_amount: uint256, _skipWholeRebalance: bool, _referral: address) ->uint256:
    """
     @notice Sender supplies assets into the market and receives yTokens in exchange
     @dev Accrues interest whether or not the operation succeeds, unless reverted
    """
    _response: Bytes[32] = raw_call(
        self.underlying_token,
        concat(
            method_id("transferFrom(address,address,uint256)"),
            convert(msg.sender, bytes32),
            convert(self, bytes32),
            convert(_amount, bytes32),
        ),
        max_outsize=32,
    )
    if len(_response) != 0:
        assert convert(_response, bool)
    value: uint256 = _amount * 10 ** 18 / self.tokenPrice
    self.total_supply += value
    self.balanceOf[msg.sender] += value

    return value


@external
def redeemIdleToken(withdrawTokens: uint256) -> uint256:
    """
     @notice Sender redeems yTokens in exchange for the underlying asset
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param withdrawTokens The number of yTokens to redeem into underlying
    """
    _value: uint256 = withdrawTokens * self.tokenPrice / 10 ** 18
    self.balanceOf[msg.sender] -= withdrawTokens
    self.total_supply -= withdrawTokens

    _response: Bytes[32] = raw_call(
        self.underlying_token,
        concat(
            method_id("transfer(address,uint256)"),
            convert(msg.sender, bytes32),
            convert(_value, bytes32),
        ),
        max_outsize=32,
    )
    if len(_response) != 0:
        assert convert(_response, bool)

    return _value


@external
def set_exchange_rate(rate: uint256):
    self.tokenPrice = rate


@external
def _set_withdrawal_fee(pct: uint256):
    # set a withdrawal fee, expressed as a percentage in bps
    self.withdrawal_fee = pct


@external
def _mint_for_testing(_target: address, _value: uint256) -> bool:
    _udecimals: uint256 = ERC20Mock(self.underlying_token).decimals()
    _underlying_value: uint256 = 2 * _value * 10 ** _udecimals / 10 ** self.decimals
    ERC20Mock(self.underlying_token)._mint_for_testing(self, _underlying_value)
    self.total_supply += _value
    self.balanceOf[_target] += _value
    log Transfer(ZERO_ADDRESS, _target, _value)

    return True
