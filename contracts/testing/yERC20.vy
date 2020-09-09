# @version 0.1.0b17
# Fake yERC20
#
# We should transfer tokens to _token_addr before wrapping
# in order to be able to get interest from somewhere
#
# WARNING
# This is for tests only and not meant to be safe to use


from vyper.interfaces import ERC20

Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

name: public(string[64])
symbol: public(string[32])
decimals: public(uint256)

balanceOf: public(map(address, uint256))
allowances: map(address, map(address, uint256))
total_supply: uint256

token: ERC20
getPricePerFullShare: public(uint256)  # yERC20 mock

@public
def __init__(_name: string[64], _symbol: string[32], _decimals: uint256, _supply: uint256,
             _token_addr: address, exchange_rate: uint256):
    init_supply: uint256 = _supply * 10 ** _decimals
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.balanceOf[msg.sender] = init_supply
    self.total_supply = init_supply
    self.token = ERC20(_token_addr)
    self.getPricePerFullShare = exchange_rate
    log.Transfer(ZERO_ADDRESS, msg.sender, init_supply)


@public
@constant
def totalSupply() -> uint256:
    """
    @dev Total number of tokens in existence.
    """
    return self.total_supply


@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    """
    @dev Function to check the amount of tokens that an owner allowed to a spender.
    @param _owner The address which owns the funds.
    @param _spender The address which will spend the funds.
    @return An uint256 specifying the amount of tokens still available for the spender.
    """
    return self.allowances[_owner][_spender]


@public
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
    log.Transfer(msg.sender, _to, _value)
    return True


@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    """
     @dev Transfer tokens from one address to another.
          Note that while this function emits a Transfer event, this is not required as per the specification,
          and other compliant implementations may not emit the event.
     @param _from address The address which you want to send tokens from
     @param _to address The address which you want to transfer to
     @param _value uint256 the amount of tokens to be transferred
    """
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    # NOTE: vyper does not allow underflows
    #      so the following subtraction would revert on insufficient allowance
    self.allowances[_from][msg.sender] -= _value
    log.Transfer(_from, _to, _value)
    return True


@public
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
    self.allowances[msg.sender][_spender] = _value
    log.Approval(msg.sender, _spender, _value)
    return True

# yERC20-specific methods
@public
def deposit(depositAmount: uint256):
    """
     @notice Sender supplies assets into the market and receives yTokens in exchange
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param depositAmount The amount of the underlying asset to supply
    """
    self.token.transferFrom(msg.sender, self, depositAmount)
    value: uint256 = depositAmount * 10 ** 18 / self.getPricePerFullShare
    self.total_supply += value
    self.balanceOf[msg.sender] += value


@public
def withdraw(withdrawTokens: uint256):
    """
     @notice Sender redeems yTokens in exchange for the underlying asset
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param withdrawTokens The number of yTokens to redeem into underlying
    """
    uvalue: uint256 = withdrawTokens * self.getPricePerFullShare / 10 ** 18
    self.balanceOf[msg.sender] -= withdrawTokens
    self.total_supply -= withdrawTokens
    self.token.transfer(msg.sender, uvalue)


@public
def set_exchange_rate(rate: uint256):
    self.getPricePerFullShare = rate


@public
def _mint_for_testing(_target: address, _value: uint256):
    self.total_supply += _value
    self.balanceOf[_target] += _value
    log.Transfer(ZERO_ADDRESS, _target, _value)
