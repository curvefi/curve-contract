# The contract which controls gauges and issuance of coins through those

WEEK: constant(uint256) = 604800  # 7 * 86400 seconds - all future times are rounded by week


struct Point:
    bias: int128
    slope: int128  # - dweight / dt
    ts: uint256

struct VotedSlope:
    slope: int128
    power: int128
    end: uint256


contract CRV20:
    def start_epoch_time_write() -> timestamp: modifying
    def start_epoch_time() -> timestamp: constant


contract VotingEscrow:
    def get_last_user_slope(addr: address) -> int128: constant
    def locked__end(addr: address) -> uint256: constant


admin: address  # Can and will be a smart contract
token: address  # CRV token
voting_escrow: address  # Voting escrow

# Gauge parameters
# All numbers are "fixed point" on the basis of 1e18
n_gauge_types: public(int128)
n_gauges: public(int128)
gauge_type_names: public(map(int128, string[64]))

# Every time a weight or epoch changes, period increases
# The idea is: relative weights are guaranteed to not change within the period
# Period 0 is reserved for "not started" (b/c default value in maps)
# Period is guaranteed to not have a change of epoch (e.g. mining rate) in the
# middle of it
period: public(int128)
period_timestamp: public(map(int128, timestamp))

gauges: public(map(int128, address))
gauge_types: public(map(address, int128))

gauge_weights: map(address, map(int128, uint256))  # address -> period -> weight
type_weights: map(int128, map(int128, uint256))  # type_id -> period -> weight
weight_sums_per_type: map(int128, map(int128, uint256))  # type_id -> period -> weight
total_weight: map(int128, uint256)  # period -> total_weight

type_last: map(int128, int128)  # Last period for type update type_id -> period
gauge_last: map(address, int128)  # Last period for gauge update gauge_addr -> period
# Total is always at the last updated state

last_epoch_time: public(timestamp)

vote_points: public(map(int128, Point))  # gauge_id -> Point
vote_enacted_at: public(map(int128, uint256))  # gauge_id -> timestamp
vote_slope_changes: public(map(int128, map(uint256, int128)))  # gauge_id -> time -> slope
vote_bias_changes: public(map(int128, map(uint256, int128)))  # gauge_id -> time -> bias
vote_user_slopes: public(map(address, map(int128, VotedSlope)))  # user -> gauge_id -> VotedSlope
vote_user_power: public(map(address, int128))  # Total vote power used by user


@public
def __init__(_token: address, _voting_escrow: address):
    self.admin = msg.sender
    self.token = _token
    self.voting_escrow = _voting_escrow
    self.n_gauge_types = 0
    self.n_gauges = 0
    self.period = 0
    self.period_timestamp[0] = block.timestamp
    self.last_epoch_time = CRV20(_token).start_epoch_time_write()


@public
def transfer_ownership(addr: address):
    assert msg.sender == self.admin
    self.admin = addr


@public
def add_type(_name: string[64]):
    assert msg.sender == self.admin
    n: int128 = self.n_gauge_types
    self.gauge_type_names[n] = _name
    self.n_gauge_types = n + 1
    # maps contain 0 values by default, no need to do anything
    # zero weights don't change other weights - no need to change last_change


@private
def change_epoch(_p: int128) -> (int128, bool):
    # Handle change of epoch
    # If epoch change happened after the last point but before current-
    #     insert a new period
    # else use the current period for both weght and epoch change
    p: int128 = _p
    let: timestamp = CRV20(self.token).start_epoch_time_write()
    epoch_changed: bool = (let > self.period_timestamp[p]) and (let <= block.timestamp)
    if epoch_changed:
        p += 1
        self.period_timestamp[p] = let
    return (p, epoch_changed)


@public
def period_write() -> int128:
    p: int128 = self.period
    epoch_changed: bool = False
    p, epoch_changed = self.change_epoch(p)
    if epoch_changed:
        self.period = p
        self.total_weight[p] = self.total_weight[p-1]
    return p


@public
def add_gauge(addr: address, gauge_type: int128, weight: uint256 = 0):
    assert msg.sender == self.admin
    assert (gauge_type >= 0) and (gauge_type < self.n_gauge_types)
    # If someone adds the same gauge twice, it will override the previous one
    # That's probably ok

    n: int128 = self.n_gauges
    self.n_gauges = n + 1

    self.gauges[n] = addr
    self.gauge_types[addr] = gauge_type

    if weight > 0:
        p: int128 = self.period
        epoch_changed: bool = False
        p, epoch_changed = self.change_epoch(p)
        p += 1
        self.period = p
        l: int128 = self.type_last[gauge_type]
        self.type_last[gauge_type] = p
        self.gauge_last[addr] = p
        old_sum: uint256 = self.weight_sums_per_type[gauge_type][l]
        _type_weight: uint256 = self.type_weights[gauge_type][l]
        if l > 0:
            # Fill historic type weights and sums
            _p: int128 = l
            for i in range(500):  # If higher (unlikely) - 0 weights
                _p += 1
                if _p == p:
                    break
                self.type_weights[gauge_type][_p] = _type_weight
                self.weight_sums_per_type[gauge_type][_p] = old_sum
        self.type_weights[gauge_type][p] = _type_weight
        self.gauge_weights[addr][p] = weight
        self.weight_sums_per_type[gauge_type][p] = weight + old_sum
        if epoch_changed:
            self.total_weight[p-1] = self.total_weight[p-2]
        self.total_weight[p] = self.total_weight[p-1] + _type_weight * weight
        self.period_timestamp[p] = block.timestamp


@public
@constant
def gauge_relative_weight(addr: address, _period: int128=-1) -> uint256:
    p: int128 = _period
    if _period < 0:
        p = self.period
    _total_weight: uint256 = self.total_weight[p]
    if _total_weight > 0:
        gauge_type: int128 = self.gauge_types[addr]
        tl: int128 = self.type_last[gauge_type]
        gl: int128 = self.gauge_last[addr]
        return 10 ** 18 * self.type_weights[gauge_type][tl] * self.gauge_weights[addr][gl] / _total_weight
    else:
        return 0


@public
def gauge_relative_weight_write(addr: address, _period: int128=-1) -> uint256:
    """
    Same as gauge_relative_weight(), but also fill all the unfilled values
    for type and gauge records
    """
    p: int128 = _period
    if _period < 0:
        p = self.period
        epoch_changed: bool = False
        p, epoch_changed = self.change_epoch(p)
        if epoch_changed:
            self.total_weight[p] = self.total_weight[p-1]
            self.period = p
    else:
        assert p <= self.period
    _total_weight: uint256 = self.total_weight[p]
    if _total_weight > 0:
        gauge_type: int128 = self.gauge_types[addr]
        tl: int128 = self.type_last[gauge_type]
        gl: int128 = self.gauge_last[addr]
        if p > tl and tl > 0:
            _type_weight: uint256 = self.type_weights[gauge_type][tl]
            old_sum: uint256 = self.weight_sums_per_type[gauge_type][tl]
            for i in range(500):
                tl += 1
                self.type_weights[gauge_type][tl] = _type_weight
                self.weight_sums_per_type[gauge_type][tl] = old_sum
                if tl == p:
                    break
            self.type_last[gauge_type] = p
        if p > gl and gl > 0:
            old_gauge_weight: uint256 = self.gauge_weights[addr][gl]
            for i in range(500):
                gl += 1
                self.gauge_weights[addr][gl] = old_gauge_weight
                if gl == p:
                    break
            self.gauge_last[addr] = p
        return 10 ** 18 * self.type_weights[gauge_type][tl] * self.gauge_weights[addr][gl] / _total_weight
    else:
        return 0


@public
def change_type_weight(type_id: int128, weight: uint256):
    assert msg.sender == self.admin

    p: int128 = self.period
    epoch_changed: bool = False
    p, epoch_changed = self.change_epoch(p)
    if epoch_changed:
        self.total_weight[p] = self.total_weight[p-1]
    p += 1
    self.period = p
    l: int128 = self.type_last[type_id]
    self.type_last[type_id] = p
    old_weight: uint256 = self.type_weights[type_id][l]
    old_sum: uint256 = self.weight_sums_per_type[type_id][l]
    old_total_weight: uint256 = self.total_weight[p-1]

    if l > 0:
        # Fill historic type weights and sums
        _p: int128 = l
        for i in range(500):  # If higher (unlikely) - 0 weights
            _p += 1
            if _p == p:
                break
            self.type_weights[type_id][_p] = old_weight
            self.weight_sums_per_type[type_id][_p] = old_sum

    self.total_weight[p] = old_total_weight + old_sum * weight - old_sum * old_weight
    self.type_weights[type_id][p] = weight
    self.weight_sums_per_type[type_id][p] = old_sum

    self.period_timestamp[p] = block.timestamp


@private
def _change_gauge_weight(addr: address, weight: uint256):
    # Fill weight from gauge_last to now, type_sums from type_last till now, total
    gauge_type: int128 = self.gauge_types[addr]
    p: int128 = self.period
    epoch_changed: bool = False
    p, epoch_changed = self.change_epoch(p)
    if epoch_changed:
        self.total_weight[p] = self.total_weight[p-1]
    p += 1
    self.period = p
    gl: int128 = self.gauge_last[addr]
    tl: int128 = self.type_last[gauge_type]
    old_gauge_weight: uint256 = self.gauge_weights[addr][gl]
    type_weight: uint256 = self.type_weights[gauge_type][tl]
    old_sum: uint256 = self.weight_sums_per_type[gauge_type][tl]
    old_total: uint256 = self.total_weight[p-1]

    if tl > 0:
        _p: int128 = tl
        for i in range(500):
            _p += 1
            if _p == p:
                break
            self.type_weights[gauge_type][_p] = type_weight
            self.weight_sums_per_type[gauge_type][_p] = old_sum
    self.type_weights[gauge_type][p] = type_weight
    self.type_last[gauge_type] = p

    if gl > 0:
        _p: int128 = gl
        for i in range(500):
            _p += 1
            if _p == p:
                break
            self.gauge_weights[addr][_p] = old_gauge_weight
    self.gauge_last[addr] = p

    new_sum: uint256 = old_sum + weight - old_gauge_weight
    self.gauge_weights[addr][p] = weight
    self.weight_sums_per_type[gauge_type][p] = new_sum
    self.total_weight[p] = old_total + new_sum * type_weight - old_sum * type_weight

    self.period_timestamp[p] = block.timestamp


@public
def change_gauge_weight(addr: address, weight: uint256):
    assert msg.sender == self.admin
    self._change_gauge_weight(addr, weight)


@private
def _enact_vote(_gauge_id: int128):
    now: uint256 = as_unitless_number(block.timestamp)
    ts: uint256 = self.vote_enacted_at[_gauge_id]

    if (ts + WEEK) / WEEK * WEEK <= block.timestamp:
        # Update vote_point
        vote_point: Point = self.vote_points[_gauge_id]
        if vote_point.ts == 0:
            vote_point.ts = now
        for i in range(500):
            next_ts: uint256 = (vote_point.ts + WEEK) / WEEK * WEEK
            dslope: int128 = 0
            if next_ts > now:
                next_ts = now
            else:
                vote_point.bias += self.vote_bias_changes[_gauge_id][next_ts]
                dslope = self.vote_slope_changes[_gauge_id][next_ts]
            vote_point.bias -= vote_point.slope * convert(next_ts - vote_point.ts, int128)
            if vote_point.bias < 0:
                vote_point.bias = 0
            vote_point.slope += dslope
            vote_point.ts = next_ts
            if next_ts == now:
                break
        self.vote_points[_gauge_id] = vote_point
        self.vote_enacted_at[_gauge_id] = now
        self._change_gauge_weight(self.gauges[_gauge_id], convert(vote_point.bias, uint256))


@public
def enact_vote(_gauge_id: int128):
    self._enact_vote(_gauge_id)


@public
def vote_for_gauge_weights(_gauge_id: int128, _user_weight: int128):
    """
    @notice Allocate voting power for changing pool weights
    @param _gauge_id Gauge which `msg.sender` votes for
    @param _user_weight Weight for a gauge in bps (units of 0.01%). Minimal is 0.01%. Ignored if 0
    """
    escrow: address = self.voting_escrow
    slope: int128 = VotingEscrow(escrow).get_last_user_slope(msg.sender)
    lock_end: uint256 = VotingEscrow(escrow).locked__end(msg.sender)
    _n_gauges: int128 = self.n_gauges
    next_time: uint256 = (as_unitless_number(block.timestamp) + WEEK) / WEEK * WEEK
    assert lock_end > next_time, "Your token lock expires too soon"
    assert (_gauge_id < _n_gauges) and (_gauge_id >= 0)  # dev: wrong gauge id
    assert (_user_weight >= 0) and (_user_weight <= 10000), "You used all your voting power"

    # Prepare slopes and biases in memory
    old_slope: VotedSlope = self.vote_user_slopes[msg.sender][_gauge_id]
    old_dt: int128 = 0
    if old_slope.end > next_time:
        old_dt = convert(old_slope.end - next_time, int128)
    old_bias: int128 = old_slope.slope * old_dt
    new_slope: VotedSlope = VotedSlope({
        slope: slope * _user_weight / 10000,
        end: lock_end,
        power: _user_weight
    })
    new_dt: int128 = convert(lock_end - next_time, int128)  # dev: raises when expired
    new_bias: int128 = new_slope.slope * new_dt

    # Check and update powers (weights) used
    power_used: int128 = self.vote_user_power[msg.sender]
    power_used += (new_slope.power - old_slope.power)
    self.vote_user_power[msg.sender] = power_used
    assert (power_used >= 0) and (power_used <= 10000), 'Used too much power'

    self._enact_vote(_gauge_id)

    ## Remove old and schedule new slope changes
    # Remove slope changes for old slopes
    # XXX schedule recording of initial slope for next_time XXX
    self.vote_bias_changes[_gauge_id][next_time] += new_bias - old_bias
    if old_slope.end > next_time:
        self.vote_slope_changes[_gauge_id][next_time] += (new_slope.slope - old_slope.slope)
    else:
        self.vote_slope_changes[_gauge_id][next_time] += new_slope.slope
    if old_slope.end > block.timestamp:
        # Cancel old slope changes if they still didn't happen
        self.vote_slope_changes[_gauge_id][old_slope.end] += old_slope.slope
    # Add slope changes for new slopes
    self.vote_slope_changes[_gauge_id][new_slope.end] -= new_slope.slope
    self.vote_user_slopes[msg.sender][_gauge_id] = new_slope


@public
def last_change() -> timestamp:
    return self.period_timestamp[self.period]


@public
def get_gauge_weight(addr: address) -> uint256:
    return self.gauge_weights[addr][self.gauge_last[addr]]


@public
def get_type_weight(type_id: int128) -> uint256:
    return self.type_weights[type_id][self.type_last[type_id]]


@public
def get_total_weight() -> uint256:
    return self.total_weight[self.period]


@public
def get_weights_sum_per_type(type_id: int128) -> uint256:
    return self.weight_sums_per_type[type_id][self.type_last[type_id]]
