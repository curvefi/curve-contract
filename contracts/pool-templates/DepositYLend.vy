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
    def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_amount: uint256): nonpayable
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
                _coin: address = self.coins[i]
                yERC20(_coin).deposit(uamount)
                amounts[i] = ERC20(_coin).balanceOf(self)
            else:
                amounts[i] = uamount

    Curve(self.curve).add_liquidity(amounts, min_mint_amount)

    _token: address = self.token
    tokens: uint256 = ERC20(_token).balanceOf(self)
    assert ERC20(_token).transfer(msg.sender, tokens)


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


@external
@nonreentrant('lock')
def remove_liquidity_one_coin(
    _token_amount: uint256,
    i: int128,
    min_uamount: uint256
):

    """
    Remove _amount of liquidity all in a form of coin i
    """
    assert ERC20(self.token).transferFrom(msg.sender, self, _token_amount)

    Curve(self.curve).remove_liquidity_one_coin(_token_amount, i, 0)

    use_lending: bool[N_COINS] = USE_LENDING
    if use_lending[i]:
        _coin: address = self.coins[i]
        _balance: uint256 = ERC20(_coin).balanceOf(self)
        yERC20(_coin).withdraw(_balance)

    _coin: address = self.underlying_coins[i]
    _balance: uint256 = ERC20(_coin).balanceOf(self)
    assert _balance >= min_uamount, "Not enough coins removed"

    _response: Bytes[32] = raw_call(
        _coin,
        concat(
            method_id("transfer(address,uint256)"),
            convert(msg.sender, bytes32),
            convert(_balance, bytes32),
        ),
        max_outsize=32,
    )
    if len(_response) > 0:
        assert convert(_response, bool)
