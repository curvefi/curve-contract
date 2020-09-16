# This gauge can be used for measuring liquidity and insurance
from vyper.interfaces import ERC20

contract CRV20:
    def start_epoch_time_write() -> timestamp: modifying
    def rate() -> uint256: constant

contract Controller:
    def period() -> int128: constant
    def period_write() -> int128: modifying
    def period_timestamp(p: int128) -> timestamp: constant
    def gauge_relative_weight(addr: address, _period: int128) -> uint256: constant
    def gauge_relative_weight_write(addr: address) -> uint256: modifying


Deposit: event({provider: indexed(address), value: uint256})
Withdraw: event({provider: indexed(address), value: uint256})


crv_token: public(address)
lp_token: public(address)
controller: public(address)
balanceOf: public(map(address, uint256))
totalSupply: public(uint256)

# The goal is to be able to calculate ∫(rate * balance / totalSupply dt) from 0 till checkpoint
# All values are kept in units of being multiplied by 1e18
period_checkpoints: timestamp[100000000000000000000000000000]
last_period: int128

# 1e18 * ∫(rate(t) / totalSupply(t) dt) from 0 till checkpoint
integrate_inv_supply: uint256[100000000000000000000000000000]  # bump epoch when rate() changes
integrate_checkpoint: timestamp

# 1e18 * ∫(rate(t) / totalSupply(t) dt) from (last_action) till checkpoint
integrate_inv_supply_of: map(address, uint256)
integrate_checkpoint_of: map(address, timestamp)


# ∫(balance * rate(t) / totalSupply(t) dt) from 0 till checkpoint
# Units: rate * t = already number of coins per address to issue
integrate_fraction: public(map(address, uint256))

inflation_rate: uint256


@public
def __init__(crv_addr: address, lp_addr: address, controller_addr: address):
    self.crv_token = crv_addr
    self.lp_token = lp_addr
    self.controller = controller_addr
    self.totalSupply = 0
    self.integrate_checkpoint = block.timestamp
    self.integrate_inv_supply[0] = 0
    period: int128 = Controller(controller_addr).period()
    self.last_period = period
    self.period_checkpoints[period] = Controller(controller_addr).period_timestamp(period)
    self.inflation_rate = CRV20(crv_addr).rate()


@private
def _checkpoint(addr: address, old_value: uint256, old_supply: uint256):
    _integrate_checkpoint: timestamp = self.integrate_checkpoint

    _token: address = self.crv_token
    _controller: address = self.controller
    old_period: int128 = self.last_period
    old_period_time: timestamp = Controller(_controller).period_timestamp(old_period)
    new_epoch: timestamp = CRV20(_token).start_epoch_time_write()
    last_weight: uint256 = Controller(_controller).gauge_relative_weight_write(self)  # Normalized to 1e18
    new_period: int128 = Controller(_controller).period()
    _integrate_inv_supply: uint256 = self.integrate_inv_supply[old_period]
    rate: uint256 = self.inflation_rate

    dt: uint256 = 0
    w: uint256 = last_weight
    # Update integral of 1/supply
    if new_period > old_period:
        # Handle going across periods where weights or rates change
        # No less than one checkpoint is expected in 1 year
        p: int128 = old_period
        for i in range(500):
            w = Controller(_controller).gauge_relative_weight(self, p)
            p += 1
            new_period_time: timestamp = Controller(_controller).period_timestamp(p)
            if _integrate_checkpoint >= new_period_time:
                # This would never happen, but if we don't do this, it'd suck if it does
                dt = 0
            elif _integrate_checkpoint >= old_period_time:
                dt = as_unitless_number(new_period_time - _integrate_checkpoint)
            else:
                dt = as_unitless_number(new_period_time - old_period_time)
            if old_supply > 0:
                _integrate_inv_supply += rate * w * dt / old_supply
            self.integrate_inv_supply[p] = _integrate_inv_supply
            if new_period_time == new_epoch:
                rate = CRV20(_token).rate()
                self.inflation_rate = rate
            old_period_time = new_period_time
            self.period_checkpoints[p] = new_period_time
            if p == new_period:
                # old_period_time contains the lastest period time here
                dt = as_unitless_number(block.timestamp - new_period_time)
                break
        self.last_period = new_period
    else:
        dt = as_unitless_number(block.timestamp - _integrate_checkpoint)
    if old_supply > 0:
        # No need to integrate if old_supply == 0
        # because no one staked then anyway
        # If old_supply == 1, we can have 1e32 dollars
        # - should be all right even if we go full Zimbabwe
        _integrate_inv_supply += rate * last_weight * dt / old_supply

    # Update user-specific integrals
    user_period: int128 = new_period
    user_period_time: timestamp = old_period_time
    user_checkpoint: timestamp = self.integrate_checkpoint_of[addr]
    _period_inv_supply: uint256 = _integrate_inv_supply
    _integrate_inv_supply_of: uint256 = self.integrate_inv_supply_of[addr]
    _integrate_fraction: uint256 = self.integrate_fraction[addr]
    # Cycle is going backwards in time
    for i in range(500):
        # Going no more than 500 periods (usually much less)
        if user_period < 0 or user_checkpoint >= user_period_time:
            # Last cycle => we are in the period of the user checkpoint
            dI: uint256 = _period_inv_supply - _integrate_inv_supply_of
            _integrate_fraction += old_value * dI / 10 ** 18
            break
        else:
            user_period -= 1
            prev_period_inv_supply: uint256 = 0
            if user_period >= 0:
                prev_period_inv_supply = self.integrate_inv_supply[user_period]
            dI: uint256 = _period_inv_supply - prev_period_inv_supply
            _period_inv_supply = prev_period_inv_supply
            if user_period >= 0:
                user_period_time = self.period_checkpoints[user_period]
            _integrate_fraction += old_value * dI / 10 ** 18

    self.integrate_inv_supply[new_period] = _integrate_inv_supply
    self.integrate_inv_supply_of[addr] = _integrate_inv_supply
    self.integrate_fraction[addr] = _integrate_fraction
    self.integrate_checkpoint_of[addr] = block.timestamp
    self.integrate_checkpoint = block.timestamp


@public
def user_checkpoint(addr: address):
    self._checkpoint(addr, self.balanceOf[addr], self.totalSupply)


@public
@nonreentrant('lock')
def deposit(value: uint256):
    old_value: uint256 = self.balanceOf[msg.sender]
    old_supply: uint256 = self.totalSupply

    self._checkpoint(msg.sender, old_value, old_supply)

    self.balanceOf[msg.sender] = old_value + value
    self.totalSupply = old_supply + value

    assert_modifiable(ERC20(self.lp_token).transferFrom(msg.sender, self, value))

    log.Deposit(msg.sender, value)


@public
@nonreentrant('lock')
def withdraw(value: uint256):
    old_value: uint256 = self.balanceOf[msg.sender]
    old_supply: uint256 = self.totalSupply

    self._checkpoint(msg.sender, old_value, old_supply)

    self.balanceOf[msg.sender] = old_value - value
    self.totalSupply = old_supply - value

    assert_modifiable(ERC20(self.lp_token).transfer(msg.sender, value))

    log.Withdraw(msg.sender, value)


# XXX make it so that if checkpoint is failing, can do a safe withdraw to escape
# the broken contract
# XXX safety switch by admin in the worst case, but better autocheck if
# _checkpoint tries to revert
