"""
This is an ERC20 with piecewise-linear mining supply.
"""

from vyper.interfaces import ERC20

implements: ERC20

Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

name: public(string[64])
symbol: public(string[32])
decimals: public(uint256)

balanceOf: public(map(address, uint256))
allowances: map(address, map(address, uint256))
total_supply: uint256

minter: public(address)
burner: public(address)
admin: public(address)

# General constants
YEAR: constant(uint256) = 86400 * 365

# Supply parameters
INITIAL_RATE: constant(uint256) = 594661989 * 10 ** 18 / YEAR  # leading to 33% premine
RATE_REDUCTION_TIME: constant(uint256) = YEAR
RATE_REDUCTION_COEFFICIENT: constant(uint256) = 1414213562373095168  # sqrt(2) * 1e18
RATE_DENOMINATOR: constant(uint256) = 10 ** 18

# Supply variables
mining_epoch: public(int128)
start_epoch_time: public(timestamp)
rate: public(uint256)

start_epoch_supply: uint256


@public
def __init__(_name: string[64], _symbol: string[32], _decimals: uint256, _supply: uint256):
    init_supply: uint256 = _supply * 10 ** _decimals
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.balanceOf[msg.sender] = init_supply
    self.total_supply = init_supply
    self.admin = msg.sender
    self.minter = msg.sender
    self.burner = msg.sender
    log.Transfer(ZERO_ADDRESS, msg.sender, init_supply)

    self.mining_epoch = 0
    self.start_epoch_time = block.timestamp
    self.rate = INITIAL_RATE
    self.start_epoch_supply = init_supply


@private
def _update_mining_parameters():
    # Any mining call must also call this if it is required

    self.start_epoch_time += RATE_REDUCTION_TIME
    self.mining_epoch += 1

    _rate: uint256 = self.rate
    self.rate = _rate * RATE_DENOMINATOR / RATE_REDUCTION_COEFFICIENT

    self.start_epoch_supply += _rate * RATE_REDUCTION_TIME


@public
def update_mining_parameters():
    # Everyone can do this but only once per epoch
    # Total supply becomes slightly larger if this function is called late
    assert block.timestamp >= self.start_epoch_time + RATE_REDUCTION_TIME
    self._update_mining_parameters()


@public
def start_epoch_time_write() -> timestamp:
    _start_epoch_time: timestamp = self.start_epoch_time
    if block.timestamp >= _start_epoch_time + RATE_REDUCTION_TIME:
        self._update_mining_parameters()
        return self.start_epoch_time
    else:
        return _start_epoch_time


@private
@constant
def _available_supply() -> uint256:
    return self.start_epoch_supply + as_unitless_number(block.timestamp - self.start_epoch_time) * self.rate


@public
@constant
def available_supply() -> uint256:
    return self._available_supply()


# XXX this might end up being not needed
@public
@constant
def mintable_in_timeframe(start: uint256, end: uint256) -> uint256:
    """
    How much supply is mintable from start timestamp till end timestamp
    """
    assert start <= end
    to_mint: uint256 = 0
    current_epoch_time: uint256 = as_unitless_number(self.start_epoch_time)
    current_rate: uint256 = self.rate

    # Special case if end is in future (not yet minted) epoch
    if end > current_epoch_time + RATE_REDUCTION_TIME:
        current_epoch_time += RATE_REDUCTION_TIME
        current_rate = current_rate * RATE_DENOMINATOR / RATE_REDUCTION_COEFFICIENT

    assert end <= current_epoch_time + RATE_REDUCTION_TIME  # Not too far in future

    for i in range(999):  # Curve will not work in 1000 years. Darn!
        if end >= current_epoch_time:
            current_end: uint256 = end
            if current_end > current_epoch_time + RATE_REDUCTION_TIME:
                current_end = current_epoch_time + RATE_REDUCTION_TIME

            current_start: uint256 = start
            if current_start >= current_epoch_time + RATE_REDUCTION_TIME:
                break  # We should never get here but what if...
            elif current_start < current_epoch_time:
                current_start = current_epoch_time

            to_mint += current_rate * (current_end - current_start)

            if start >= current_epoch_time:
                break

        current_epoch_time -= RATE_REDUCTION_TIME
        current_rate = current_rate * RATE_REDUCTION_COEFFICIENT / RATE_DENOMINATOR  # double-division with rounding made rate a bit less => good
        assert current_rate <= INITIAL_RATE  # This should never happen

    return to_mint


@public
def set_minter(_minter: address):
    assert msg.sender == self.admin
    self.minter = _minter


@public
def set_admin(_admin: address):
    assert msg.sender == self.admin
    self.admin = _admin


@public
def set_burner(_burner: address):
    assert msg.sender == self.admin
    self.burner = _burner


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
    if msg.sender != self.minter:  # minter is allowed to transfer anything
        # NOTE: vyper does not allow underflows
        # so the following subtraction would revert on insufficient allowance
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
    assert _value == 0 or self.allowances[msg.sender][_spender] == 0
    self.allowances[msg.sender][_spender] = _value
    log.Approval(msg.sender, _spender, _value)
    return True


@public
def mint(_to: address, _value: uint256):
    """
    @dev Mint an amount of the token and assigns it to an account.
         This encapsulates the modification of balances such that the
         proper events are emitted.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    assert msg.sender == self.minter
    assert _to != ZERO_ADDRESS

    if block.timestamp >= self.start_epoch_time + RATE_REDUCTION_TIME:
        self._update_mining_parameters()

    _total_supply: uint256 = self.total_supply + _value
    assert _total_supply <= self._available_supply()
    self.total_supply = _total_supply

    self.balanceOf[_to] += _value
    log.Transfer(ZERO_ADDRESS, _to, _value)


@private
def _burn(_to: address, _value: uint256):
    """
    @dev Internal function that burns an amount of the token of a given
         account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    assert _to != ZERO_ADDRESS
    self.total_supply -= _value
    self.balanceOf[_to] -= _value
    log.Transfer(_to, ZERO_ADDRESS, _value)


@public
def burn(_value: uint256):
    """
    @dev Burn an amount of the token of msg.sender.
    @param _value The amount that will be burned.
    """
    assert msg.sender == self.burner, "Only burner is allowed to burn"
    self._burn(msg.sender, _value)


@public
def burnFrom(_to: address, _value: uint256):
    """
    @dev Burn an amount of the token from a given account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    assert msg.sender == self.burner, "Only burner is allowed to burn"
    self._burn(_to, _value)


@public
def set_name(_name: string[64], _symbol: string[32]):
    assert msg.sender == self.admin, "Only admin is allowed to change name"
    self.name = _name
    self.symbol = _symbol
