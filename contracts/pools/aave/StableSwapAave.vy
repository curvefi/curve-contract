# @version 0.2.7
"""
@title Curve aPool
@author Curve.Fi
@license Copyright (c) Curve.Fi, 2020 - all rights reserved
@notice Pool implementation with aToken-style lending
"""

from vyper.interfaces import ERC20


interface aToken:
    def redeem(_amount: uint256): nonpayable

interface CurveToken:
    def mint(_to: address, _value: uint256) -> bool: nonpayable
    def burnFrom(_to: address, _value: uint256) -> bool: nonpayable


# Events
event TokenExchange:
    buyer: indexed(address)
    sold_id: int128
    tokens_sold: uint256
    bought_id: int128
    tokens_bought: uint256

event TokenExchangeUnderlying:
    buyer: indexed(address)
    sold_id: int128
    tokens_sold: uint256
    bought_id: int128
    tokens_bought: uint256

event AddLiquidity:
    provider: indexed(address)
    token_amounts: uint256[N_COINS]
    fees: uint256[N_COINS]
    invariant: uint256
    token_supply: uint256

event RemoveLiquidity:
    provider: indexed(address)
    token_amounts: uint256[N_COINS]
    fees: uint256[N_COINS]
    token_supply: uint256

event RemoveLiquidityOne:
    provider: indexed(address)
    token_amount: uint256
    coin_amount: uint256

event RemoveLiquidityImbalance:
    provider: indexed(address)
    token_amounts: uint256[N_COINS]
    fees: uint256[N_COINS]
    invariant: uint256
    token_supply: uint256

event CommitNewAdmin:
    deadline: indexed(uint256)
    admin: indexed(address)

event NewAdmin:
    admin: indexed(address)

event CommitNewFee:
    deadline: indexed(uint256)
    fee: uint256
    admin_fee: uint256
    offpeg_fee_multiplier: uint256

event NewFee:
    fee: uint256
    admin_fee: uint256
    offpeg_fee_multiplier: uint256

event RampA:
    old_A: uint256
    new_A: uint256
    initial_time: uint256
    future_time: uint256

event StopRampA:
    A: uint256
    t: uint256


# These constants must be set prior to compiling
N_COINS: constant(int128) = 3
PRECISION_MUL: constant(uint256[N_COINS]) = [1, 1000000000000, 1000000000000]

# fixed constants
FEE_DENOMINATOR: constant(uint256) = 10 ** 10
LENDING_PRECISION: constant(uint256) = 10 ** 18
PRECISION: constant(uint256) = 10 ** 18  # The precision to convert to

MAX_ADMIN_FEE: constant(uint256) = 10 * 10 ** 9
MAX_FEE: constant(uint256) = 5 * 10 ** 9
MAX_A: constant(uint256) = 10 ** 6
MAX_A_CHANGE: constant(uint256) = 10

ADMIN_ACTIONS_DELAY: constant(uint256) = 3 * 86400
MIN_RAMP_TIME: constant(uint256) = 86400

coins: public(address[N_COINS])
underlying_coins: public(address[N_COINS])
admin_balances: public(uint256[N_COINS])

fee: public(uint256)  # fee * 1e10
offpeg_fee_multiplier: public(uint256)  # * 1e10
admin_fee: public(uint256)  # admin_fee * 1e10

owner: public(address)
lp_token: public(address)

aave_lending_pool: address
aave_referral: uint256

A_PRECISION: constant(uint256) = 100
initial_A: public(uint256)
future_A: public(uint256)
initial_A_time: public(uint256)
future_A_time: public(uint256)

admin_actions_deadline: public(uint256)
transfer_ownership_deadline: public(uint256)
future_fee: public(uint256)
future_admin_fee: public(uint256)
future_offpeg_fee_multiplier: public(uint256)  # * 1e10
future_owner: public(address)

is_killed: bool
kill_deadline: uint256
KILL_DEADLINE_DT: constant(uint256) = 2 * 30 * 86400


@external
def __init__(_coins: address[N_COINS],
             _underlying_coins: address[N_COINS],
             _pool_token: address,
             _aave_lending_pool: address,
             _A: uint256, _fee: uint256):
    """
    _coins: Addresses of ERC20 conracts of coins (c-tokens) involved
    _pool_token: Address of the token representing LP share
    _A: Amplification coefficient multiplied by n * (n - 1)
    _fee: Fee to charge for exchanges
    """
    for i in range(N_COINS):
        assert _coins[i] != ZERO_ADDRESS
        assert _underlying_coins[i] != ZERO_ADDRESS
    self.coins = _coins
    self.underlying_coins = _underlying_coins
    self.initial_A = _A
    self.future_A = _A
    self.fee = _fee
    self.owner = msg.sender
    self.kill_deadline = block.timestamp + KILL_DEADLINE_DT
    self.lp_token = _pool_token
    self.aave_lending_pool = _aave_lending_pool


@view
@internal
def _A() -> uint256:
    """
    Handle ramping A up or down
    """
    t1: uint256 = self.future_A_time
    A1: uint256 = self.future_A

    if block.timestamp < t1:
        A0: uint256 = self.initial_A
        t0: uint256 = self.initial_A_time
        # Expressions in uint256 cannot have negative numbers, thus "if"
        if A1 > A0:
            return A0 + (A1 - A0) * (block.timestamp - t0) / (t1 - t0)
        else:
            return A0 - (A0 - A1) * (block.timestamp - t0) / (t1 - t0)

    else:  # when t1 == 0 or block.timestamp >= t1
        return A1


@view
@external
def A() -> uint256:
    return self._A()


@pure
@internal
def _dynamic_fee(xpi: uint256, xpj: uint256, _fee: uint256, _feemul: uint256) -> uint256:
    if _feemul <= FEE_DENOMINATOR:
        return _fee
    else:
        xps2: uint256 = (xpi + xpj)
        xps2 *= xps2  # Doing just ** 2 can overflow apparently
        return (_feemul * _fee) / (
            (_feemul - FEE_DENOMINATOR) * 4 * xpi * xpj / xps2 + \
            FEE_DENOMINATOR)


@view
@external
def dynamic_fee(i: int128, j: int128) -> uint256:
    precisions: uint256[N_COINS] = PRECISION_MUL
    xpi: uint256 = (ERC20(self.coins[i]).balanceOf(self) - self.admin_balances[i]) * precisions[i]
    xpj: uint256 = (ERC20(self.coins[j]).balanceOf(self) - self.admin_balances[j]) * precisions[j]
    return self._dynamic_fee(xpi, xpj, self.fee, self.offpeg_fee_multiplier)


@view
@external
def balances(i: int128) -> uint256:
    return ERC20(self.coins[i]).balanceOf(self) - self.admin_balances[i]


@view
@internal
def _balances() -> uint256[N_COINS]:
    result: uint256[N_COINS] = empty(uint256[N_COINS])
    for i in range(N_COINS):
        result[i] = ERC20(self.coins[i]).balanceOf(self) - self.admin_balances[i]
    return result


@pure
@internal
def get_D(xp: uint256[N_COINS], amp: uint256) -> uint256:
    """
    D invariant calculation in non-overflowing integer operations
    iteratively

    A * sum(x_i) * n**n + D = A * D * n**n + D**(n+1) / (n**n * prod(x_i))

    Converging solution:
    D[j+1] = (A * n**n * sum(x_i) - D[j]**(n+1) / (n**n prod(x_i))) / (A * n**n - 1)
    """
    S: uint256 = 0

    for _x in xp:
        S += _x
    if S == 0:
        return 0

    Dprev: uint256 = 0
    D: uint256 = S
    Ann: uint256 = amp * N_COINS
    for _i in range(255):
        D_P: uint256 = D
        for _x in xp:
            D_P = D_P * D / (_x * N_COINS + 1)  # +1 is to prevent /0
        Dprev = D
        D = (Ann * S + D_P * N_COINS) * D / ((Ann - 1) * D + (N_COINS + 1) * D_P)
        # Equality with the precision of 1
        if D > Dprev:
            if D - Dprev <= 1:
                break
        else:
            if Dprev - D <= 1:
                break
    return D


@view
@internal
def get_D_precisions(coin_balances: uint256[N_COINS], amp: uint256) -> uint256:
    xp: uint256[N_COINS] = PRECISION_MUL
    for i in range(N_COINS):
        xp[i] *= coin_balances[i]
    return self.get_D(xp, amp)


@view
@external
def get_virtual_price() -> uint256:
    """
    Returns portfolio virtual price (for calculating profit)
    scaled up by 1e18
    """
    D: uint256 = self.get_D_precisions(self._balances(), self._A())
    # D is in the units similar to DAI (e.g. converted to precision 1e18)
    # When balanced, D = n * x_u - total virtual value of the portfolio
    token_supply: uint256 = ERC20(self.lp_token).totalSupply()
    return D * PRECISION / token_supply


@view
@external
def calc_token_amount(amounts: uint256[N_COINS], deposit: bool) -> uint256:
    """
    Simplified method to calculate addition or reduction in token supply at
    deposit or withdrawal without taking fees into account (but looking at
    slippage).
    Needed to prevent front-running, not for precise calculations!
    """
    coin_balances: uint256[N_COINS] = self._balances()
    amp: uint256 = self._A()
    D0: uint256 = self.get_D_precisions(coin_balances, amp)
    for i in range(N_COINS):
        if deposit:
            coin_balances[i] += amounts[i]
        else:
            coin_balances[i] -= amounts[i]
    D1: uint256 = self.get_D_precisions(coin_balances, amp)
    token_amount: uint256 = ERC20(self.lp_token).totalSupply()
    diff: uint256 = 0
    if deposit:
        diff = D1 - D0
    else:
        diff = D0 - D1
    return diff * token_amount / D0


@external
@nonreentrant('lock')
def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256):
    # Amounts is amounts of c-tokens
    assert not self.is_killed  # dev: is killed

    fees: uint256[N_COINS] = empty(uint256[N_COINS])
    _fee: uint256 = self.fee * N_COINS / (4 * (N_COINS - 1))
    _feemul: uint256 = self.offpeg_fee_multiplier
    _admin_fee: uint256 = self.admin_fee
    amp: uint256 = self._A()

    token_supply: uint256 = ERC20(self.lp_token).totalSupply()
    # Initial invariant
    D0: uint256 = 0
    old_balances: uint256[N_COINS] = self._balances()
    if token_supply != 0:
        D0 = self.get_D_precisions(old_balances, amp)
    new_balances: uint256[N_COINS] = old_balances

    for i in range(N_COINS):
        if token_supply == 0:
            assert amounts[i] != 0  # dev: initial deposit requires all coins
        new_balances[i] = old_balances[i] + amounts[i]

    # Invariant after change
    D1: uint256 = self.get_D_precisions(new_balances, amp)
    assert D1 > D0

    ys: uint256 = (D0 + D1) / N_COINS

    # We need to recalculate the invariant accounting for fees
    # to calculate fair user's share
    D2: uint256 = D1
    if token_supply != 0:
        # Only account for fees if we are not the first to deposit
        for i in range(N_COINS):
            ideal_balance: uint256 = D1 * old_balances[i] / D0
            difference: uint256 = 0
            if ideal_balance > new_balances[i]:
                difference = ideal_balance - new_balances[i]
            else:
                difference = new_balances[i] - ideal_balance
            xs: uint256 = old_balances[i] + new_balances[i]
            fees[i] = self._dynamic_fee(xs, ys, _fee, _feemul) * difference / FEE_DENOMINATOR
            if _admin_fee != 0:
                self.admin_balances[i] += fees[i] * _admin_fee / FEE_DENOMINATOR
            new_balances[i] -= fees[i]
        D2 = self.get_D_precisions(new_balances, amp)

    # Calculate, how much pool tokens to mint
    mint_amount: uint256 = 0
    if token_supply == 0:
        mint_amount = D1  # Take the dust if there was any
    else:
        mint_amount = token_supply * (D2 - D0) / D0

    assert mint_amount >= min_mint_amount, "Slippage screwed you"

    # Take coins from the sender
    for i in range(N_COINS):
        if amounts[i] != 0:
            assert ERC20(self.coins[i]).transferFrom(msg.sender, self, amounts[i]) # dev: failed transfer

    # Mint pool tokens
    CurveToken(self.lp_token).mint(msg.sender, mint_amount)

    log AddLiquidity(msg.sender, amounts, fees, D1, token_supply + mint_amount)


@view
@internal
def get_y(i: int128, j: int128, x: uint256, xp: uint256[N_COINS]) -> uint256:
    """
    Calculate x[j] if one makes x[i] = x

    Done by solving quadratic equation iteratively.
    x_1**2 + x1 * (sum' - (A*n**n - 1) * D / (A * n**n)) = D ** (n + 1) / (n ** (2 * n) * prod' * A)
    x_1**2 + b*x_1 = c

    x_1 = (x_1**2 + c) / (2*x_1 + b)
    """
    # x in the input is converted to the same price/precision

    assert i != j       # dev: same coin
    assert j >= 0       # dev: j below zero
    assert j < N_COINS  # dev: j above N_COINS

    # should be unreachable, but good for safety
    assert i >= 0
    assert i < N_COINS

    amp: uint256 = self._A()
    D: uint256 = self.get_D(xp, amp)
    c: uint256 = D
    S_: uint256 = 0
    Ann: uint256 = amp * N_COINS

    _x: uint256 = 0
    for _i in range(N_COINS):
        if _i == i:
            _x = x
        elif _i != j:
            _x = xp[_i]
        else:
            continue
        S_ += _x
        c = c * D / (_x * N_COINS)
    c = c * D / (Ann * N_COINS)
    b: uint256 = S_ + D / Ann  # - D
    y_prev: uint256 = 0
    y: uint256 = D
    for _i in range(255):
        y_prev = y
        y = (y*y + c) / (2 * y + b - D)
        # Equality with the precision of 1
        if y > y_prev:
            if y - y_prev <= 1:
                break
        else:
            if y_prev - y <= 1:
                break
    return y


@pure
@internal
def get_y_D(A_: uint256, i: int128, xp: uint256[N_COINS], D: uint256) -> uint256:
    """
    Calculate x[i] if one reduces D from being calculated for xp to D

    Done by solving quadratic equation iteratively.
    x_1**2 + x1 * (sum' - (A*n**n - 1) * D / (A * n**n)) = D ** (n + 1) / (n ** (2 * n) * prod' * A)
    x_1**2 + b*x_1 = c

    x_1 = (x_1**2 + c) / (2*x_1 + b)
    """
    # x in the input is converted to the same price/precision

    assert i >= 0       # dev: i below zero
    assert i < N_COINS  # dev: i above N_COINS

    c: uint256 = D
    S_: uint256 = 0
    Ann: uint256 = A_ * N_COINS

    _x: uint256 = 0
    for _i in range(N_COINS):
        if _i != i:
            _x = xp[_i]
        else:
            continue
        S_ += _x
        c = c * D / (_x * N_COINS)
    c = c * D / (Ann * N_COINS)
    b: uint256 = S_ + D / Ann
    y_prev: uint256 = 0
    y: uint256 = D
    for _i in range(255):
        y_prev = y
        y = (y*y + c) / (2 * y + b - D)
        # Equality with the precision of 1
        if y > y_prev:
            if y - y_prev <= 1:
                break
        else:
            if y_prev - y <= 1:
                break
    return y


@view
@internal
def _calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256:
    # First, need to calculate
    # * Get current D
    # * Solve Eqn against y_i for D - _token_amount
    A_: uint256 = self._A()
    _fee: uint256 = self.fee * N_COINS / (4 * (N_COINS - 1))
    feemul: uint256 = self.offpeg_fee_multiplier
    precisions: uint256[N_COINS] = PRECISION_MUL
    total_supply: uint256 = ERC20(self.lp_token).totalSupply()

    xp: uint256[N_COINS] = self._balances()
    S: uint256 = 0
    for j in range(N_COINS):
        xp[j] *= precisions[j]
        S += xp[j]

    D0: uint256 = self.get_D(xp, A_)
    D1: uint256 = D0 - _token_amount * D0 / total_supply
    xp_reduced: uint256[N_COINS] = xp
    ys: uint256 = (D0 + D1) / (2 * N_COINS)

    new_y: uint256 = self.get_y_D(A_, i, xp, D1)

    for j in range(N_COINS):
        dx_expected: uint256 = 0
        xavg: uint256 = 0
        if j == i:
            dx_expected = xp[j] * D1 / D0 - new_y
            xavg = (xp[j] + new_y) / 2
        else:
            dx_expected = xp[j] - xp[j] * D1 / D0
            xavg = xp[j]
        xp_reduced[j] -= self._dynamic_fee(xavg, ys, _fee, feemul) * dx_expected / FEE_DENOMINATOR

    dy: uint256 = xp_reduced[i] - self.get_y_D(A_, i, xp_reduced, D1)
    dy = dy / precisions[i]

    return dy


@view
@external
def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256:
    return self._calc_withdraw_one_coin(_token_amount, i)


@external
@nonreentrant('lock')
def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_uamount: uint256):
    """
    Remove _amount of liquidity all in a form of coin i
    """
    assert not self.is_killed  # dev: is killed

    dy: uint256 = self._calc_withdraw_one_coin(_token_amount, i)
    assert dy >= min_uamount, "Not enough coins removed"

    CurveToken(self.lp_token).burnFrom(msg.sender, _token_amount)  # dev: insufficient funds
    assert ERC20(self.coins[i]).transfer(msg.sender, dy)

    log RemoveLiquidityOne(msg.sender, _token_amount, dy)


@view
@external
def get_dy(i: int128, j: int128, dx: uint256) -> uint256:
    # dx and dy in c-units
    precisions: uint256[N_COINS] = PRECISION_MUL
    xp: uint256[N_COINS] = self._balances()
    for k in range(N_COINS):
        xp[k] *= precisions[k]

    x: uint256 = xp[i] + dx * precisions[i]
    y: uint256 = self.get_y(i, j, x, xp)
    dy: uint256 = (xp[j] - y) / precisions[j]
    _fee: uint256 = self._dynamic_fee(
            (xp[i] + x) / 2, (xp[j] + y) / 2, self.fee, self.offpeg_fee_multiplier
        ) * dy / FEE_DENOMINATOR
    return dy - _fee


@internal
def _exchange(i: int128, j: int128, dx: uint256) -> uint256:
    assert not self.is_killed  # dev: is killed
    # dx and dy are in c-tokens

    xp: uint256[N_COINS] = self._balances()
    precisions: uint256[N_COINS] = PRECISION_MUL
    for k in range(N_COINS):
        xp[k] *= precisions[k]

    x: uint256 = xp[i] + dx * precisions[i]
    y: uint256 = self.get_y(i, j, x, xp)
    dy: uint256 = xp[j] - y
    dy_fee: uint256 = dy * self._dynamic_fee(
            (xp[i] + x) / 2, (xp[j] + y) / 2, self.fee, self.offpeg_fee_multiplier
        ) / FEE_DENOMINATOR

    _admin_fee: uint256 = self.admin_fee
    if _admin_fee != 0:
        dy_admin_fee: uint256 = dy_fee * _admin_fee / FEE_DENOMINATOR
        if dy_admin_fee != 0:
            self.admin_balances[j] += dy_admin_fee / precisions[j]

    _dy: uint256 = (dy - dy_fee) / precisions[j]

    return _dy


@external
@nonreentrant('lock')
def exchange(i: int128, j: int128, dx: uint256, min_dy: uint256):
    dy: uint256 = self._exchange(i, j, dx)
    assert dy >= min_dy, "Exchange resulted in fewer coins than expected"

    assert ERC20(self.coins[i]).transferFrom(msg.sender, self, dx)
    assert ERC20(self.coins[j]).transfer(msg.sender, dy)

    log TokenExchange(msg.sender, i, dx, j, dy)


@external
@nonreentrant('lock')
def exchange_underlying(i: int128, j: int128, dx: uint256, min_dy: uint256):
    dy: uint256 = self._exchange(i, j, dx)
    assert dy >= min_dy, "Exchange resulted in fewer coins than expected"

    u_coin_i: address = self.underlying_coins[i]
    u_coin_j: address = self.underlying_coins[j]
    coin_j: address = self.coins[j]
    lending_pool: address = self.aave_lending_pool

    # transfer underlying coin from msg.sender to self
    _response: Bytes[32] = raw_call(
        u_coin_i,
        concat(
            method_id("transferFrom(address,address,uint256)"),
            convert(msg.sender, bytes32),
            convert(self, bytes32),
            convert(dx, bytes32)
        ),
        max_outsize=32
    )
    if len(_response) != 0:
        assert convert(_response, bool)

    # approve transfer of underlying coin to aave lending pool
    _response = raw_call(
        u_coin_i,
        concat(
            method_id("approve(address,uint256)"),
            convert(lending_pool, bytes32),
            convert(dx, bytes32)
        ),
        max_outsize=32
    )
    if len(_response) != 0:
        assert convert(_response, bool)

    # deposit to aave lending pool
    raw_call(
        lending_pool,
        concat(
            method_id("deposit(address,uint256,uint16)"),
            convert(u_coin_i, bytes32),
            convert(dx, bytes32),
            convert(self.aave_referral, bytes32),
        )
    )
    aToken(coin_j).redeem(dy)

    _response = raw_call(
        u_coin_j,
        concat(
            method_id("transfer(address,uint256)"),
            convert(msg.sender, bytes32),
            convert(dy, bytes32)
        ),
        max_outsize=32
    )
    if len(_response) != 0:
        assert convert(_response, bool)

    log TokenExchangeUnderlying(msg.sender, i, dx, j, dy)


@external
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]):
    total_supply: uint256 = ERC20(self.lp_token).totalSupply()
    CurveToken(self.lp_token).burnFrom(msg.sender, _amount)  # dev: insufficient funds

    fees: uint256[N_COINS] = empty(uint256[N_COINS])
    amounts: uint256[N_COINS] = self._balances()

    for i in range(N_COINS):
        value: uint256 = amounts[i] * _amount / total_supply
        assert value >= min_amounts[i], "Withdrawal resulted in fewer coins than expected"
        amounts[i] = value
        assert ERC20(self.coins[i]).transfer(msg.sender, value)

    log RemoveLiquidity(msg.sender, amounts, fees, total_supply - _amount)


@external
@nonreentrant('lock')
def remove_liquidity_imbalance(amounts: uint256[N_COINS], max_burn_amount: uint256):
    assert not self.is_killed  # dev: is killed

    token_supply: uint256 = ERC20(self.lp_token).totalSupply()
    assert token_supply != 0  # dev: zero total supply

    _fee: uint256 = self.fee * N_COINS / (4 * (N_COINS - 1))
    _feemul: uint256 = self.offpeg_fee_multiplier
    _admin_fee: uint256 = self.admin_fee
    amp: uint256 = self._A()

    old_balances: uint256[N_COINS] = self._balances()
    new_balances: uint256[N_COINS] = old_balances
    D0: uint256 = self.get_D_precisions(old_balances, amp)
    for i in range(N_COINS):
        new_balances[i] -= amounts[i]
    D1: uint256 = self.get_D_precisions(new_balances, amp)
    ys: uint256 = (D0 + D1) / N_COINS
    fees: uint256[N_COINS] = empty(uint256[N_COINS])
    for i in range(N_COINS):
        ideal_balance: uint256 = D1 * old_balances[i] / D0
        difference: uint256 = 0
        if ideal_balance > new_balances[i]:
            difference = ideal_balance - new_balances[i]
        else:
            difference = new_balances[i] - ideal_balance
        xs: uint256 = new_balances[i] + old_balances[i]
        fees[i] = self._dynamic_fee(xs, ys, _fee, _feemul) * difference / FEE_DENOMINATOR
        if _admin_fee != 0:
            self.admin_balances[i] += fees[i] * _admin_fee / FEE_DENOMINATOR
        new_balances[i] -= fees[i]
    D2: uint256 = self.get_D_precisions(new_balances, amp)

    token_amount: uint256 = (D0 - D2) * token_supply / D0
    assert token_amount != 0  # dev: zero tokens burned
    assert token_amount <= max_burn_amount, "Slippage screwed you"

    CurveToken(self.lp_token).burnFrom(msg.sender, token_amount)  # dev: insufficient funds
    for i in range(N_COINS):
        assert ERC20(self.coins[i]).transfer(msg.sender, amounts[i])

    log RemoveLiquidityImbalance(msg.sender, amounts, fees, D1, token_supply - token_amount)


### Admin functions ###
@external
def ramp_A(_future_A: uint256, _future_time: uint256):
    assert msg.sender == self.owner  # dev: only owner
    assert _future_time >= block.timestamp + MIN_RAMP_TIME  # dev: insufficient time

    _initial_A: uint256 = self._A()
    self.initial_A = _initial_A
    self.future_A = _future_A
    self.initial_A_time = block.timestamp
    self.future_A_time = _future_time

    log RampA(_initial_A, _future_A, block.timestamp, _future_time)


@external
def stop_ramp_A():
    assert msg.sender == self.owner  # dev: only owner

    current_A: uint256 = self._A()
    self.initial_A = current_A
    self.future_A = current_A
    self.initial_A_time = 0
    self.future_A_time = 0

    log StopRampA(current_A, block.timestamp)


@external
def commit_new_fee(new_fee: uint256, new_admin_fee: uint256, new_offpeg_fee_multiplier: uint256):
    assert msg.sender == self.owner  # dev: only owner
    assert self.admin_actions_deadline == 0  # dev: active action
    assert new_fee <= MAX_FEE  # dev: fee exceeds maximum
    assert new_admin_fee <= MAX_ADMIN_FEE  # dev: admin fee exceeds maximum
    assert new_offpeg_fee_multiplier * new_fee <= MAX_FEE * FEE_DENOMINATOR  # dev: offpeg multiplier exceeds maximum

    _deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY
    self.admin_actions_deadline = _deadline
    self.future_fee = new_fee
    self.future_admin_fee = new_admin_fee
    self.future_offpeg_fee_multiplier = new_offpeg_fee_multiplier

    log CommitNewFee(_deadline, new_fee, new_admin_fee, new_offpeg_fee_multiplier)


@external
def apply_new_fee():
    assert msg.sender == self.owner  # dev: only owner
    assert block.timestamp >= self.admin_actions_deadline  # dev: insufficient time
    assert self.admin_actions_deadline != 0  # dev: no active action

    self.admin_actions_deadline = 0
    _fee: uint256 = self.future_fee
    _admin_fee: uint256 = self.future_admin_fee
    _fml: uint256 = self.future_offpeg_fee_multiplier
    self.fee = _fee
    self.admin_fee = _admin_fee
    self.offpeg_fee_multiplier = _fml

    log NewFee(_fee, _admin_fee, _fml)


@external
def revert_new_parameters():
    assert msg.sender == self.owner  # dev: only owner

    self.admin_actions_deadline = 0


@external
def commit_transfer_ownership(_owner: address):
    assert msg.sender == self.owner  # dev: only owner
    assert self.transfer_ownership_deadline == 0  # dev: active transfer

    _deadline: uint256 = block.timestamp + ADMIN_ACTIONS_DELAY
    self.transfer_ownership_deadline = _deadline
    self.future_owner = _owner

    log CommitNewAdmin(_deadline, _owner)


@external
def apply_transfer_ownership():
    assert msg.sender == self.owner  # dev: only owner
    assert block.timestamp >= self.transfer_ownership_deadline  # dev: insufficient time
    assert self.transfer_ownership_deadline != 0  # dev: no active transfer

    self.transfer_ownership_deadline = 0
    _owner: address = self.future_owner
    self.owner = _owner

    log NewAdmin(_owner)


@external
def revert_transfer_ownership():
    assert msg.sender == self.owner  # dev: only owner

    self.transfer_ownership_deadline = 0


@external
def withdraw_admin_fees():
    assert msg.sender == self.owner  # dev: only owner

    for i in range(N_COINS):
        value: uint256 = self.admin_balances[i]
        if value != 0:
            assert ERC20(self.coins[i]).transfer(msg.sender, value)
            self.admin_balances[i] = 0


@external
def donate_admin_fees():
    """
    Just in case admin balances somehow become higher than total (rounding error?)
    this can be used to fix the state, too
    """
    assert msg.sender == self.owner  # dev: only owner
    self.admin_balances = empty(uint256[N_COINS])


@external
def kill_me():
    assert msg.sender == self.owner  # dev: only owner
    assert self.kill_deadline > block.timestamp  # dev: deadline has passed
    self.is_killed = True


@external
def unkill_me():
    assert msg.sender == self.owner  # dev: only owner
    self.is_killed = False


@external
def set_aave_referral(referral_code: uint256):
    assert msg.sender == self.owner  # dev: only owner
    assert referral_code < 2 ** 16  # dev: uint16 overflow
    self.aave_referral = referral_code
