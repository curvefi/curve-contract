# A "zap" to work with SUSD pool
# (c) Curve.Fi, 2020
from vyper.interfaces import ERC20
import yERC20 as yERC20

# Pool looks like [ySUSD, [yDAI, yUSDC, yUSDT, yTUSD]]
# Implements (in plain coins):
# * add_liquidity
# * remove_liquidity
# * remove_liquidity_imbalance
# * remove_liquidity_one_coin
# * exchange
# * exchange_underlying
# * get_dy_underlying
# * get_dy
# * Events for exchanges?
# * Use ypool's zap to withdraw one coin from there?

N_COINS: constant(int128) = 2
N_COINS_Y: constant(int128) = 4
N_COINS_CURVED: constant(int128) = 5

# Tether transfer-only ABI
contract USDT:
    def transfer(_to: address, _value: uint256): modifying
    def transferFrom(_from: address, _to: address, _value: uint256): modifying


contract Curve:
    def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256): modifying
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]): modifying
    def remove_liquidity_imbalance(amounts: uint256[N_COINS], max_burn_amount: uint256): modifying
    def balances(i: int128) -> uint256: constant
    def A() -> uint256: constant
    def fee() -> uint256: constant
    def owner() -> address: constant
    def coins(i: int128) -> address: constant
    def underlying_coins(i: int128) -> address: constant
    def get_virtual_price() -> uint256: constant
    def donate_dust(amounts: uint256[N_COINS]): modifying
    def calc_token_amount(amounts: uint256[N_COINS], deposit: bool) -> uint256: constant
    def get_dy(i: int128, j: int128, dx: uint256) -> uint256: constant


contract YCurve:
    def add_liquidity(amounts: uint256[N_COINS_Y], min_mint_amount: uint256): modifying
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS_Y]): modifying
    def remove_liquidity_imbalance(amounts: uint256[N_COINS_Y], max_burn_amount: uint256): modifying
    def balances(i: int128) -> uint256: constant
    def A() -> uint256: constant
    def fee() -> uint256: constant
    def owner() -> address: constant
    def coins(i: int128) -> address: constant
    def underlying_coins(i: int128) -> address: constant
    def calc_token_amount(amounts: uint256[N_COINS_Y], deposit: bool) -> uint256: constant
    def get_dy(i: int128, j: int128, dx: uint256) -> uint256: constant


contract YZap:
    def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256: constant


TETHERED: constant(bool[N_COINS_CURVED]) = [False, False, False, True, False]
ZERO256: constant(uint256) = 0  # This hack is really bad XXX
ZEROS: constant(uint256[N_COINS]) = [ZERO256, ZERO256]
ZEROS_Y: constant(uint256[N_COINS_Y]) = [ZERO256, ZERO256, ZERO256, ZERO256]
ZEROS_CURVED: constant(uint256[N_COINS_CURVED]) = [ZERO256, ZERO256, ZERO256, ZERO256, ZERO256]
LENDING_PRECISION: constant(uint256) = 10 ** 18
PRECISION: constant(uint256) = 10 ** 18
ONE256: constant(uint256) = 1  # Oh man, here we go XXX
PRECISION_OUTER_MUL: constant(uint256[N_COINS]) = [ONE256, ONE256]
PRECISION_MUL: constant(uint256[N_COINS_CURVED]) = ___PRECISION_MUL___
FEE_DENOMINATOR: constant(uint256) = 10 ** 10
FEE_IMPRECISION: constant(uint256) = 25 * 10 ** 8  # % of the fee

coins: public(address[N_COINS_CURVED])
underlying_coins: public(address[N_COINS_CURVED])

curve: public(address)
token: public(address)

ycurve: public(address)
ytoken: public(address)
yzap: public(address)


@public
def __init__(_coins: address[N_COINS], _underlying_coins: address[N_COINS],
             _curve: address, _token: address, _yzap: address):

    for i in range(N_COINS - 1):
        self.coins[i] = _coins[i]
        self.underlying_coins[i] = _underlying_coins[i]

    self.ycurve = _underlying_coins[N_COINS - 1]
    self.ytoken = _coins[N_COINS - 1]

    for i in range(N_COINS - 1, N_COINS_CURVED):
        j: int128 = i + 1 - N_COINS
        self.coins[i] = Curve(_underlying_coins[N_COINS-1]).coins(j)
        self.underlying_coins[i] = Curve(_underlying_coins[N_COINS-1]).underlying_coins(j)

    self.curve = _curve
    self.token = _token
    self.yzap = _yzap


@public
@nonreentrant('lock')
def add_liquidity(uamounts: uint256[N_COINS_CURVED], min_mint_amount: uint256):
    tethered: bool[N_COINS_CURVED] = TETHERED
    amounts: uint256[N_COINS_CURVED] = ZEROS_CURVED
    _curve: address = self.curve
    _token: address = self.token
    _ycurve: address = self.ycurve
    _ytoken: address = self.ytoken

    for i in range(N_COINS_CURVED):
        uamount: uint256 = uamounts[i]

        if uamount > 0:
            # Transfer the underlying coin from owner
            if tethered[i]:
                USDT(self.underlying_coins[i]).transferFrom(
                    msg.sender, self, uamount)
            else:
                assert_modifiable(ERC20(self.underlying_coins[i])\
                    .transferFrom(msg.sender, self, uamount))

            # Mint if needed
            ERC20(self.underlying_coins[i]).approve(self.coins[i], uamount)
            yERC20(self.coins[i]).deposit(uamount)
            amounts[i] = yERC20(self.coins[i]).balanceOf(self)
            if i < N_COINS - 1:
                ERC20(self.coins[i]).approve(_curve, amounts[i])
            else:
                ERC20(self.coins[i]).approve(_ycurve, amounts[i])
    # Now we have self owning amounts[] of ycoins, approved to both Curve contracts

    amounts_inner: uint256[N_COINS_Y] = ZEROS_Y
    for i in range(N_COINS-1, N_COINS_CURVED):
        amounts_inner[i - (N_COINS - 1)] = amounts[i]
    YCurve(_ycurve).add_liquidity(amounts_inner, 0)
    ytoken_amount: uint256 = ERC20(_ytoken).balanceOf(self)

    amounts_outer: uint256[N_COINS] = ZEROS
    for i in range(N_COINS-1):
        amounts_outer[i] = amounts[i]
    amounts_outer[N_COINS-1] = ytoken_amount

    Curve(_curve).add_liquidity(amounts_outer, min_mint_amount)

    tokens: uint256 = ERC20(_token).balanceOf(self)
    assert_modifiable(ERC20(_token).transfer(msg.sender, tokens))


@private
def _send_all(_addr: address, min_uamounts: uint256[N_COINS_CURVED], one: int128):
    tethered: bool[N_COINS_CURVED] = TETHERED

    for i in range(N_COINS_CURVED):
        if (one < 0) or (i == one):
            _coin: address = self.coins[i]
            _balance: uint256 = yERC20(_coin).balanceOf(self)
            if _balance == 0:  # Do nothing for 0 coins
                continue
            yERC20(_coin).withdraw(_balance)

            _ucoin: address = self.underlying_coins[i]
            _uamount: uint256 = ERC20(_ucoin).balanceOf(self)
            assert _uamount >= min_uamounts[i], "Not enough coins withdrawn"

            if tethered[i]:
                USDT(_ucoin).transfer(_addr, _uamount)
            else:
                assert_modifiable(ERC20(_ucoin).transfer(_addr, _uamount))


@public
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, min_uamounts: uint256[N_COINS_CURVED]):
    assert_modifiable(ERC20(self.token).transferFrom(msg.sender, self, _amount))

    # First - withdraw outer coins
    zeros: uint256[N_COINS] = ZEROS
    Curve(self.curve).remove_liquidity(_amount, zeros)

    yamount: uint256 = ERC20(self.ytoken).balanceOf(self)
    zeros_y: uint256[N_COINS_Y] = ZEROS_Y
    YCurve(self.ycurve).remove_liquidity(yamount, zeros_y)

    self._send_all(msg.sender, min_uamounts, -1)


@public
@nonreentrant('lock')
def remove_liquidity_imbalance(uamounts: uint256[N_COINS_CURVED], max_burn_amount: uint256):
    """
    Get max_burn_amount in, remove requested liquidity and transfer back what is left
    """
    _token: address = self.token
    _ytoken: address = self.ytoken
    _curve: address = self.curve
    _ycurve: address = self.ycurve

    amounts: uint256[N_COINS_CURVED] = uamounts
    for i in range(N_COINS_CURVED):
        if amounts[i] > 0:
            rate: uint256 = yERC20(self.coins[i]).getPricePerFullShare()
            amounts[i] = amounts[i] * LENDING_PRECISION / rate

    # Transfrer max tokens in
    _tokens: uint256 = ERC20(_token).balanceOf(msg.sender)
    if _tokens > max_burn_amount:
        _tokens = max_burn_amount
    assert_modifiable(ERC20(_token).transferFrom(msg.sender, self, _tokens))

    # Now this is tricky.
    # * We calculate token amount needed for Y with over-estimation
    # * Remove that token amount and sUSD
    # * Remove individual coins other than sUSD from that Y Token
    # * Deposit the rest of ytoken back to the pool
    # * Return the rest of pool token back to the sender
    # Phew. Expensive!

    # So, calculate (the excessive) amount of ytokens to remove...
    yfee: uint256 = YCurve(_ycurve).fee()
    yamounts: uint256[N_COINS_Y] = ZEROS_Y
    withdraw_y: bool = False
    for i in range(N_COINS_Y):
        j: int128 = i + N_COINS - 1
        if amounts[j] > 0:
            withdraw_y = True
            yamounts[j] = amounts[i]
    ytokens: uint256 = 0
    if withdraw_y:
        ytokens = YCurve(_ycurve).calc_token_amount(yamounts, False)
        ytokens = ytokens + ytokens * yfee / FEE_DENOMINATOR

    # Remove those amounts from the outer pool
    outer_amounts: uint256[N_COINS] = ZEROS
    for i in range(N_COINS - 1):
        outer_amounts[i] = amounts[i]
    outer_amounts[N_COINS-1] = ytokens
    Curve(_curve).remove_liquidity_imbalance(outer_amounts, max_burn_amount)

    # Remove yamounts from from ypool
    if withdraw_y:
        YCurve(_ycurve).remove_liquidity_imbalance(yamounts, ytokens)
        # Add the rest of ytokens back
        yback: uint256[N_COINS] = ZEROS
        yback[N_COINS-1] = ERC20(_ytoken).balanceOf(self)
        Curve(_curve).add_liquidity(yback, 0)

    # Transfer unused tokens back
    _tokens = ERC20(_token).balanceOf(self)
    assert_modifiable(ERC20(_token).transfer(msg.sender, _tokens))

    # Unwrap and transfer all the coins we've got
    self._send_all(msg.sender, ZEROS_CURVED, -1)


@private
@constant
def get_D(A: uint256, xp: uint256[N_COINS]) -> uint256:
    S: uint256 = 0
    for _x in xp:
        S += _x
    if S == 0:
        return 0

    Dprev: uint256 = 0
    D: uint256 = S
    Ann: uint256 = A * N_COINS
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


@private
@constant
def get_y(A: uint256, i: int128, _xp: uint256[N_COINS], D: uint256) -> uint256:
    """
    Calculate x[i] if one reduces D from being calculated for _xp to D

    Done by solving quadratic equation iteratively.
    x_1**2 + x1 * (sum' - (A*n**n - 1) * D / (A * n**n)) = D ** (n + 1) / (n ** (2 * n) * prod' * A)
    x_1**2 + b*x_1 = c

    x_1 = (x_1**2 + c) / (2*x_1 + b)
    """
    # x in the input is converted to the same price/precision

    assert (i >= 0) and (i < N_COINS)

    c: uint256 = D
    S_: uint256 = 0
    Ann: uint256 = A * N_COINS

    _x: uint256 = 0
    for _i in range(N_COINS):
        if _i != i:
            _x = _xp[_i]
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


@private
@constant
def _calc_withdraw_one_coin(_token_amount: uint256, k: int128, rates: uint256[N_COINS]) -> uint256[2]:
    # First, need to calculate
    # * Get current D
    # * Solve Eqn against y_i for D - _token_amount
    crv: address = self.curve
    A: uint256 = Curve(crv).A()
    fee: uint256 = Curve(crv).fee() * N_COINS / (4 * (N_COINS - 1))
    fee += fee * FEE_IMPRECISION / FEE_DENOMINATOR  # Overcharge to account for imprecision
    precisions: uint256[N_COINS] = PRECISION_OUTER_MUL
    total_supply: uint256 = ERC20(self.token).totalSupply()

    i: int128 = k
    if i >= N_COINS:
        i = N_COINS - 1
    # if k <= N_COINS-1: proceed as we did
    # if k >= N_COINS-1: calculate number of ytoken, then call another zap to get ytoken number

    xp: uint256[N_COINS] = PRECISION_OUTER_MUL
    S: uint256 = 0
    for j in range(N_COINS):
        xp[j] *= Curve(crv).balances(j)
        xp[j] = xp[j] * rates[j] / LENDING_PRECISION
        S += xp[j]

    D0: uint256 = self.get_D(A, xp)
    D1: uint256 = D0 - _token_amount * D0 / total_supply
    xp_reduced: uint256[N_COINS] = xp

    # xp = xp - fee * | xp * D1 / D0 - (xp - S * dD / D0 * (0, ... 1, ..0))|
    for j in range(N_COINS):
        dx_expected: uint256 = 0
        b_ideal: uint256 = xp[j] * D1 / D0
        b_expected: uint256 = xp[j]
        if j == i:
            b_expected -= S * (D0 - D1) / D0
        if b_ideal >= b_expected:
            dx_expected += (b_ideal - b_expected)
        else:
            dx_expected += (b_expected - b_ideal)
        xp_reduced[j] -= fee * dx_expected / FEE_DENOMINATOR

    dy: uint256 = xp_reduced[i] - self.get_y(A, i, xp_reduced, D1)

    dy_inner: uint256 = 0
    if i == N_COINS - 1:
        dy = dy * LENDING_PRECISION / rates[N_COINS-1]  # YToken
        dy_inner = YZap(self.yzap).calc_withdraw_one_coin(dy, k - (N_COINS-1))
    else:
        dy = dy / precisions[i]  # Plain assets - plain results

    return [dy, dy_inner]


@public
@constant
def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256:
    rates: uint256[N_COINS] = ZEROS

    for j in range(N_COINS-1):
        rates[j] = yERC20(self.coins[j]).getPricePerFullShare()
    rates[N_COINS-1] = Curve(self.curve).get_virtual_price()

    dys: uint256[2] = self._calc_withdraw_one_coin(_token_amount, i, rates)
    if dys[1] == 0:
        return dys[0]
    else:
        return dys[1]


@public
@constant
def calc_token_amount(amounts: uint256[N_COINS_CURVED], deposit: bool) -> uint256:
    # amounts are compounded
    amounts_inner: uint256[N_COINS_Y] = ZEROS_Y
    amounts_outer: uint256[N_COINS] = ZEROS

    y_needed: bool = False
    for i in range(N_COINS_Y):
        amounts_inner[i] = amounts[N_COINS - 1 + i]
        if amounts_inner[i] > 0:
            y_needed = True

    ypool_token: uint256 = 0
    if y_needed:
        ypool_token = YCurve(self.ycurve).calc_token_amount(amounts_inner, deposit)

    for i in range(N_COINS-1):
        amounts_outer[i] = amounts[i]
    amounts_outer[N_COINS-1] = ypool_token

    return Curve(self.curve).calc_token_amount(amounts_outer, deposit)


@public
@constant
def get_dy(i: int128, j: int128, dx: uint256) -> uint256:
    assert (i >= N_COINS-1) or (j >= N_COINS-1)

    if i < N_COINS-1:
        # In outer pool -> out of inner pool
        dytoken_amount: uint256 = Curve(self.curve).get_dy(i, N_COINS-1, dx)
        dy: uint256 = YZap(self.yzap).calc_withdraw_one_coin(dytoken_amount, j - (N_COINS-1))
        return dy * LENDING_PRECISION / yERC20(self.coins[j]).getPricePerFullShare()

    else:
        # Deposit to inner pool -> get out of outer pool
        amounts: uint256[N_COINS_Y] = ZEROS_Y
        amounts[i - (N_COINS-1)] = dx
        dytoken_amount: uint256 = YCurve(self.ycurve).calc_token_amount(amounts, True)
        dy: uint256 = Curve(self.curve).get_dy(N_COINS-1, j, dytoken_amount)
        return dy


@public
@constant
def get_dy_underlying(i: int128, j: int128, dx: uint256) -> uint256:
    pass


@public
@nonreentrant('lock')
def exchange(i: int128, j: int128, dx: uint256, min_dy: uint256):
    pass


@public
@nonreentrant('lock')
def exchange_underlying(i: int128, j: int128, dx: uint256, min_dy: uint256):
    pass


@public
@nonreentrant('lock')
def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_uamount: uint256, donate_dust: bool = False):
    """
    Remove _amount of liquidity all in a form of coin i
    """
    rates: uint256[N_COINS] = ZEROS
    _curve: address = self.curve
    _token: address = self.token
    _ytoken: address = self.ytoken
    k: int128 = i
    if k >= N_COINS:
        k = N_COINS - 1

    for j in range(N_COINS-1):
        rates[j] = yERC20(self.coins[j]).getPricePerFullShare()
    rates[N_COINS-1] = Curve(self.curve).get_virtual_price()

    # [dy_outer, dy_inner]
    dys: uint256[2] = self._calc_withdraw_one_coin(_token_amount, i, rates)
    dy_outer: uint256 = dys[0]
    dy_inner: uint256 = dys[1]
    dy: uint256 = 0
    if dy_inner == 0:
        dy = dy_outer
    else:
        dy = dy_inner
    assert dy >= min_uamount, "Not enough coins removed"

    assert_modifiable(
        ERC20(self.token).transferFrom(msg.sender, self, _token_amount))

    # First, remove any asset we need from SCurve pool
    amounts: uint256[N_COINS] = ZEROS
    if k == N_COINS - 1:
        amounts[k] = dy_outer  # YToken
    else:
        amounts[k] = dy_outer * LENDING_PRECISION / rates[k]  # Compounded
    token_amount_before: uint256 = ERC20(_token).balanceOf(self)
    Curve(_curve).remove_liquidity_imbalance(amounts, _token_amount)

    if k == N_COINS - 1:
        # We need to withdraw from YToken
        inner_amounts: uint256[N_COINS_Y] = ZEROS_Y
        rate: uint256 = yERC20(self.coins[i]).getPricePerFullShare()
        inner_amounts[i - (N_COINS - 1)] = dy_inner * LENDING_PRECISION / rate
        YCurve(self.ycurve).remove_liquidity_imbalance(inner_amounts, dy_outer)
        # We have some YToken dust, and we can donate it to LPs
        amounts[k] = ERC20(_ytoken).balanceOf(self)
        if amounts[k] > 0:
            ERC20(_ytoken).approve(_curve, amounts[k])
            Curve(_curve).donate_dust(amounts)

    # Unwrap and transfer all the coins we've got
    # And we really got only i-th coin
    self._send_all(msg.sender, ZEROS_CURVED, i)

    if not donate_dust:
        # Transfer unused tokens back
        token_amount_after: uint256 = ERC20(_token).balanceOf(self)
        if token_amount_after > token_amount_before:
            assert_modifiable(ERC20(_token).transfer(
                msg.sender, token_amount_after - token_amount_before)
            )


@public
@nonreentrant('lock')
def withdraw_donated_dust():
    owner: address = Curve(self.curve).owner()
    assert msg.sender == owner

    _token: address = self.token
    assert_modifiable(
        ERC20(_token).transfer(owner, ERC20(_token).balanceOf(self)))
