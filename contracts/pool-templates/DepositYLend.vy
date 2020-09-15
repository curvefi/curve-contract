# @version ^0.2.0
"""
@title "Zap" Depositer for Yearn-style lending tokens
@author Curve.Fi
@license Copyright (c) Curve.Fi, 2020 - all rights reserved
@notice deposit/withdraw Curve contract without too many transactions
@dev This contract is only a template, pool-specific constants
     must be set prior to compiling
"""

from vyper.interfaces import ERC20

# External Contracts
interface yERC20:
    def deposit(depositAmount: uint256): nonpayable
    def withdraw(withdrawTokens: uint256): nonpayable
    def getPricePerFullShare() -> uint256: view

interface Curve:
    def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]): nonpayable
    def remove_liquidity_imbalance(amounts: uint256[N_COINS], max_burn_amount: uint256): nonpayable
    def balances(i: int128) -> uint256: view
    def A() -> uint256: view
    def fee() -> uint256: view
    def owner() -> address: view


# These constants must be set prior to compiling
N_COINS: constant(int128) = ___N_COINS___
PRECISION_MUL: constant(uint256[N_COINS]) = ___PRECISION_MUL___
USE_LENDING: constant(bool[N_COINS]) = ___USE_LENDING___

# Fixed constants
LENDING_PRECISION: constant(uint256) = 10 ** 18
PRECISION: constant(uint256) = 10 ** 18
FEE_DENOMINATOR: constant(uint256) = 10 ** 10
FEE_IMPRECISION: constant(uint256) = 25 * 10 ** 8  # % of the fee

coins: public(address[N_COINS])
underlying_coins: public(address[N_COINS])
curve: public(address)
token: public(address)


@external
def __init__(
    _coins: address[N_COINS],
    _underlying_coins: address[N_COINS],
    _curve: address,
    _token: address
):
    for i in range(N_COINS):
        assert _coins[i] != ZERO_ADDRESS
        assert _underlying_coins[i] != ZERO_ADDRESS

        # approve underlying and wrapped coins for infinite transfers
        _response: Bytes[32] = raw_call(
            _underlying_coins[i],
            concat(
                method_id("approve(address,uint256)"),
                convert(_coins[i], bytes32),
                convert(MAX_UINT256, bytes32),
            ),
            max_outsize=32,
        )
        if len(_response) > 0:
            assert convert(_response, bool)
        _response = raw_call(
            _coins[i],
            concat(
                method_id("approve(address,uint256)"),
                convert(_curve, bytes32),
                convert(MAX_UINT256, bytes32),
            ),
            max_outsize=32,
        )
        if len(_response) > 0:
            assert convert(_response, bool)

    self.coins = _coins
    self.underlying_coins = _underlying_coins
    self.curve = _curve
    self.token = _token


@external
@nonreentrant('lock')
def add_liquidity(uamounts: uint256[N_COINS], min_mint_amount: uint256):
    use_lending: bool[N_COINS] = USE_LENDING
    amounts: uint256[N_COINS] = empty(uint256[N_COINS])

    for i in range(N_COINS):
        uamount: uint256 = uamounts[i]

        if uamount != 0:
            # Transfer the underlying coin from owner
            _response: Bytes[32] = raw_call(
                self.underlying_coins[i],
                concat(
                    method_id("transferFrom(address,address,uint256)"),
                    convert(msg.sender, bytes32),
                    convert(self, bytes32),
                    convert(uamount, bytes32)
                ),
                max_outsize=32
            )
            if len(_response) > 0:
                assert convert(_response, bool)

            # Mint if needed
            if use_lending[i]:
                yERC20(self.coins[i]).deposit(uamount)
                amounts[i] = ERC20(self.coins[i]).balanceOf(self)
            else:
                amounts[i] = uamount

    Curve(self.curve).add_liquidity(amounts, min_mint_amount)

    tokens: uint256 = ERC20(self.token).balanceOf(self)
    assert ERC20(self.token).transfer(msg.sender, tokens)


@internal
def _send_all(_addr: address, min_uamounts: uint256[N_COINS], one: int128):
    use_lending: bool[N_COINS] = USE_LENDING

    for i in range(N_COINS):
        if (one < 0) or (i == one):
            if use_lending[i]:
                _coin: address = self.coins[i]
                _balance: uint256 = ERC20(_coin).balanceOf(self)
                if _balance == 0:  # Do nothing if there are 0 coins
                    continue
                yERC20(_coin).withdraw(_balance)

            _ucoin: address = self.underlying_coins[i]
            _uamount: uint256 = ERC20(_ucoin).balanceOf(self)
            assert _uamount >= min_uamounts[i], "Not enough coins withdrawn"

            # Send only if we have something to send
            if _uamount != 0:
                _response: Bytes[32] = raw_call(
                    _ucoin,
                    concat(
                        method_id("transfer(address,uint256)"),
                        convert(_addr, bytes32),
                        convert(_uamount, bytes32)
                    ),
                    max_outsize=32
                )
                if len(_response) > 0:
                    assert convert(_response, bool)


@external
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, min_uamounts: uint256[N_COINS]):
    assert ERC20(self.token).transferFrom(msg.sender, self, _amount)
    Curve(self.curve).remove_liquidity(_amount, empty(uint256[N_COINS]))

    self._send_all(msg.sender, min_uamounts, -1)


@external
@nonreentrant('lock')
def remove_liquidity_imbalance(uamounts: uint256[N_COINS], max_burn_amount: uint256):
    """
    Get max_burn_amount in, remove requested liquidity and transfer back what is left
    """
    use_lending: bool[N_COINS] = USE_LENDING
    _token: address = self.token

    amounts: uint256[N_COINS] = uamounts
    for i in range(N_COINS):
        if use_lending[i] and amounts[i] > 0:
            rate: uint256 = yERC20(self.coins[i]).getPricePerFullShare()
            amounts[i] = amounts[i] * LENDING_PRECISION / rate
        # if not use_lending - all good already

    # Transfrer max tokens in
    _tokens: uint256 = ERC20(_token).balanceOf(msg.sender)
    if _tokens > max_burn_amount:
        _tokens = max_burn_amount
    assert ERC20(_token).transferFrom(msg.sender, self, _tokens)

    Curve(self.curve).remove_liquidity_imbalance(amounts, max_burn_amount)

    # Transfer unused tokens back
    _tokens = ERC20(_token).balanceOf(self)
    assert ERC20(_token).transfer(msg.sender, _tokens)

    # Unwrap and transfer all the coins we've got
    self._send_all(msg.sender, empty(uint256[N_COINS]), -1)


@internal
@view
def _xp_mem(rates: uint256[N_COINS], _balances: uint256[N_COINS]) -> uint256[N_COINS]:
    result: uint256[N_COINS] = rates
    for i in range(N_COINS):
        result[i] = result[i] * _balances[i] / PRECISION
    return result


@internal
@view
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


@internal
@view
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


@internal
@view
def _calc_withdraw_one_coin(_token_amount: uint256, i: int128, rates: uint256[N_COINS]) -> uint256:
    # First, need to calculate
    # * Get current D
    # * Solve Eqn against y_i for D - _token_amount
    use_lending: bool[N_COINS] = USE_LENDING
    crv: address = self.curve
    A: uint256 = Curve(crv).A()
    fee: uint256 = Curve(crv).fee() * N_COINS / (4 * (N_COINS - 1))
    fee += fee * FEE_IMPRECISION / FEE_DENOMINATOR  # Overcharge to account for imprecision
    precisions: uint256[N_COINS] = PRECISION_MUL
    total_supply: uint256 = ERC20(self.token).totalSupply()

    xp: uint256[N_COINS] = PRECISION_MUL
    S: uint256 = 0
    for j in range(N_COINS):
        xp[j] *= Curve(crv).balances(j)
        if use_lending[j]:
            # Use stored rate b/c we have imprecision anyway
            xp[j] = xp[j] * rates[j] / LENDING_PRECISION
        S += xp[j]
        # if not use_lending - all good already

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
            dx_expected = (b_ideal - b_expected)
        else:
            dx_expected = (b_expected - b_ideal)
        xp_reduced[j] -= fee * dx_expected / FEE_DENOMINATOR

    dy: uint256 = xp_reduced[i] - self.get_y(A, i, xp_reduced, D1)
    dy = dy / precisions[i]

    return dy


@external
@view
def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256:
    rates: uint256[N_COINS] = empty(uint256[N_COINS])
    use_lending: bool[N_COINS] = USE_LENDING

    for j in range(N_COINS):
        if use_lending[j]:
            rates[j] = yERC20(self.coins[j]).getPricePerFullShare()
        else:
            rates[j] = 10 ** 18

    return self._calc_withdraw_one_coin(_token_amount, i, rates)


@external
@nonreentrant('lock')
def remove_liquidity_one_coin(
    _token_amount: uint256,
    i: int128,
    min_uamount: uint256,
    donate_dust: bool = False
):
    """
    Remove _amount of liquidity all in a form of coin i
    """
    use_lending: bool[N_COINS] = USE_LENDING
    rates: uint256[N_COINS] = empty(uint256[N_COINS])
    _token: address = self.token

    for j in range(N_COINS):
        if use_lending[j]:
            rates[j] = yERC20(self.coins[j]).getPricePerFullShare()
        else:
            rates[j] = LENDING_PRECISION

    dy: uint256 = self._calc_withdraw_one_coin(_token_amount, i, rates)
    assert dy >= min_uamount, "Not enough coins removed"

    assert ERC20(self.token).transferFrom(msg.sender, self, _token_amount)

    amounts: uint256[N_COINS] = empty(uint256[N_COINS])
    amounts[i] = dy * LENDING_PRECISION / rates[i]
    token_amount_before: uint256 = ERC20(_token).balanceOf(self)
    Curve(self.curve).remove_liquidity_imbalance(amounts, _token_amount)

    # Unwrap and transfer all the coins we've got
    self._send_all(msg.sender, empty(uint256[N_COINS]), i)

    if not donate_dust:
        # Transfer unused tokens back
        token_amount_after: uint256 = ERC20(_token).balanceOf(self)
        if token_amount_after > token_amount_before:
            assert ERC20(_token).transfer(msg.sender, token_amount_after - token_amount_before)


@external
@nonreentrant('lock')
def withdraw_donated_dust():
    owner: address = Curve(self.curve).owner()
    assert msg.sender == owner

    _token: address = self.token
    assert ERC20(_token).transfer(owner, ERC20(_token).balanceOf(self))
