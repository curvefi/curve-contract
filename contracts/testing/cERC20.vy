# @version ^0.2.0
"""
@notice Mock cERC20
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
exchangeRateStored: public(uint256)
supplyRatePerBlock: public(uint256)
accrualBlockNumber: public(uint256)

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

    _udecimals: uint256 = ERC20Mock(_underlying_token).decimals()
    self.exchangeRateStored = 10**(18 + _udecimals -_decimals)
    self.accrualBlockNumber = block.number


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
    if self.balanceOf[msg.sender] < _value:
        # cToken return False on a failed transfer instead of reverting
        return False
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    if self.balanceOf[_from] < _value or self.allowances[_from][msg.sender] < _value:
        return False
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


# cERC20-specific functions
@external
def mint(mintAmount: uint256) -> uint256:
    """
     @notice Sender supplies assets into the market and receives cTokens in exchange
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param mintAmount The amount of the underlying asset to supply
     @return uint 0=success, otherwise a failure
    """
    _response: Bytes[32] = raw_call(
        self.underlying_token,
        concat(
            method_id("transferFrom(address,address,uint256)"),
            convert(msg.sender, bytes32),
            convert(self, bytes32),
            convert(mintAmount, bytes32),
        ),
        max_outsize=32,
    )
    value: uint256 = mintAmount * 10**18 / self.exchangeRateStored
    self.total_supply += value
    self.balanceOf[msg.sender] += value
    return 0


@external
def redeem(redeemTokens: uint256) -> uint256:
    """
     @notice Sender redeems cTokens in exchange for the underlying asset
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param redeemTokens The number of cTokens to redeem into underlying
     @return uint 0=success, otherwise a failure
    """
    value: uint256 = redeemTokens * self.exchangeRateStored / 10**18
    self.balanceOf[msg.sender] -= redeemTokens
    self.total_supply -= redeemTokens
    _response: Bytes[32] = raw_call(
        self.underlying_token,
        concat(
            method_id("transfer(address,uint256)"),
            convert(msg.sender, bytes32),
            convert(value, bytes32),
        ),
        max_outsize=32,
    )
    if len(_response) != 0:
        assert convert(_response, bool)

    return 0


@external
def exchangeRateCurrent() -> uint256:
    # Simulate blockchain write
    rate: uint256 = self.exchangeRateStored
    self.exchangeRateStored = rate

    return rate


@external
def set_exchange_rate(rate: uint256):
    self.exchangeRateStored = rate

    expected: uint256 = self.total_supply * self.exchangeRateStored / 10**18
    actual: uint256 = ERC20(self.underlying_token).balanceOf(self)

    if expected > actual:
        # make sure we have enough of the underlying asset based on the rate change
        ERC20Mock(self.underlying_token)._mint_for_testing(self, expected - actual)


@external
def _mint_for_testing(_target: address, _value: uint256) -> bool:
    underlying_value: uint256 = _value * self.exchangeRateStored / 10**18

    ERC20Mock(self.underlying_token)._mint_for_testing(self, underlying_value)
    self.total_supply += _value
    self.balanceOf[_target] += _value
    log Transfer(ZERO_ADDRESS, _target, _value)

    return True
