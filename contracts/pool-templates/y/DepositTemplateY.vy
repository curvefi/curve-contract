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
    def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256) -> uint256: nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]) -> uint256[N_COINS]: nonpayable
    def remove_liquidity_imbalance(amounts: uint256[N_COINS], max_burn_amount: uint256) -> uint256: nonpayable
    def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_amount: uint256) -> uint256: nonpayable
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
lp_token: public(address)


@external
def __init__(
    _coins: address[N_COINS],
    _underlying_coins: address[N_COINS],
    _curve: address,
    _token: address
):
    """
    @notice Contract constructor
    @dev Where a token does not use wrapping, use the same address
         for `_coins` and `_underlying_coins`
    @param _coins List of wrapped coin addresses
    @param _underlying_coins List of underlying coin addresses
    @param _curve Pool address
    @param _token Pool LP token address
    """
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
    self.lp_token = _token


@external
@nonreentrant('lock')
def add_liquidity(_underlying_amounts: uint256[N_COINS], _min_mint_amount: uint256) -> uint256:
    """
    @notice Wrap underlying coins and deposit them in the pool
    @param _underlying_amounts List of amounts of underlying coins to deposit
    @param _min_mint_amount Minimum amount of LP tokens to mint from the deposit
    @return Amount of LP tokens received by depositing
    """
    use_lending: bool[N_COINS] = USE_LENDING
    wrapped_amounts: uint256[N_COINS] = empty(uint256[N_COINS])

    for i in range(N_COINS):
        amount: uint256 = _underlying_amounts[i]

        if amount != 0:
            # Transfer the underlying coin from owner
            _response: Bytes[32] = raw_call(
                self.underlying_coins[i],
                concat(
                    method_id("transferFrom(address,address,uint256)"),
                    convert(msg.sender, bytes32),
                    convert(self, bytes32),
                    convert(amount, bytes32)
                ),
                max_outsize=32
            )
            if len(_response) > 0:
                assert convert(_response, bool)

            # Mint if needed
            if use_lending[i]:
                coin: address = self.coins[i]
                yERC20(coin).deposit(amount)
                wrapped_amounts[i] = ERC20(coin).balanceOf(self)
            else:
                wrapped_amounts[i] = amount

    Curve(self.curve).add_liquidity(wrapped_amounts, _min_mint_amount)

    lp_token: address = self.lp_token
    lp_amount: uint256 = ERC20(lp_token).balanceOf(self)
    assert ERC20(lp_token).transfer(msg.sender, lp_amount)

    return lp_amount


@internal
def _unwrap_and_transfer(_addr: address, _min_amounts: uint256[N_COINS]) -> uint256[N_COINS]:
    # unwrap coins and transfer them to the sender
    use_lending: bool[N_COINS] = USE_LENDING
    _amounts: uint256[N_COINS] = empty(uint256[N_COINS])

    for i in range(N_COINS):
        if use_lending[i]:
            _coin: address = self.coins[i]
            _balance: uint256 = ERC20(_coin).balanceOf(self)
            if _balance == 0:  # Do nothing if there are 0 coins
                continue
            yERC20(_coin).withdraw(_balance)

        _ucoin: address = self.underlying_coins[i]
        _uamount: uint256 = ERC20(_ucoin).balanceOf(self)
        assert _uamount >= _min_amounts[i], "Not enough coins withdrawn"

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
            _amounts[i] = _uamount

    return _amounts

@external
@nonreentrant('lock')
def remove_liquidity(
    _amount: uint256,
    _min_underlying_amounts: uint256[N_COINS]
) -> uint256[N_COINS]:
    """
    @notice Withdraw and unwrap coins from the pool
    @dev Withdrawal amounts are based on current deposit ratios
    @param _amount Quantity of LP tokens to burn in the withdrawal
    @param _min_underlying_amounts Minimum amounts of underlying coins to receive
    @return List of amounts of underlying coins that were withdrawn
    """
    assert ERC20(self.lp_token).transferFrom(msg.sender, self, _amount)
    Curve(self.curve).remove_liquidity(_amount, empty(uint256[N_COINS]))

    return self._unwrap_and_transfer(msg.sender, _min_underlying_amounts)


@external
@nonreentrant('lock')
def remove_liquidity_imbalance(
    _underlying_amounts: uint256[N_COINS],
    _max_burn_amount: uint256
) -> uint256[N_COINS]:
    """
    @notice Withdraw and unwrap coins from the pool in an imbalanced amount
    @dev Amounts in `_underlying_amounts` correspond to withdrawn amounts
         before any fees charge for unwrapping.
    @param _underlying_amounts List of amounts of underlying coins to withdraw
    @param _max_burn_amount Maximum amount of LP token to burn in the withdrawal
    @return List of amounts of underlying coins that were withdrawn
    """
    use_lending: bool[N_COINS] = USE_LENDING
    lp_token: address = self.lp_token

    amounts: uint256[N_COINS] = _underlying_amounts
    for i in range(N_COINS):
        _amount: uint256 = amounts[i]
        if use_lending[i] and _amount > 0:
            rate: uint256 = yERC20(self.coins[i]).getPricePerFullShare()
            amounts[i] = _amount * LENDING_PRECISION / rate
        # if not use_lending - all good already

    # Transfer max tokens in
    _lp_amount: uint256 = ERC20(lp_token).balanceOf(msg.sender)
    if _lp_amount > _max_burn_amount:
        _lp_amount = _max_burn_amount
    assert ERC20(lp_token).transferFrom(msg.sender, self, _lp_amount)

    Curve(self.curve).remove_liquidity_imbalance(amounts, _max_burn_amount)

    # Transfer unused LP tokens back
    _lp_amount = ERC20(lp_token).balanceOf(self)
    if _lp_amount != 0:
        assert ERC20(lp_token).transfer(msg.sender, _lp_amount)

    # Unwrap and transfer all the coins we've got
    return self._unwrap_and_transfer(msg.sender, empty(uint256[N_COINS]))


@external
@nonreentrant('lock')
def remove_liquidity_one_coin(
    _amount: uint256,
    i: int128,
    _min_underlying_amount: uint256
) -> uint256:
    """
    @notice Withdraw and unwrap a single coin from the pool
    @param _amount Amount of LP tokens to burn in the withdrawal
    @param i Index value of the coin to withdraw
    @param _min_underlying_amount Minimum amount of underlying coin to receive
    @return Amount of underlying coin received
    """
    assert ERC20(self.lp_token).transferFrom(msg.sender, self, _amount)

    Curve(self.curve).remove_liquidity_one_coin(_amount, i, 0)

    use_lending: bool[N_COINS] = USE_LENDING
    if use_lending[i]:
        coin: address = self.coins[i]
        _balance: uint256 = ERC20(coin).balanceOf(self)
        yERC20(coin).withdraw(_balance)

    coin: address = self.underlying_coins[i]
    _balance: uint256 = ERC20(coin).balanceOf(self)
    assert _balance >= _min_underlying_amount, "Not enough coins removed"

    _response: Bytes[32] = raw_call(
        coin,
        concat(
            method_id("transfer(address,uint256)"),
            convert(msg.sender, bytes32),
            convert(_balance, bytes32),
        ),
        max_outsize=32,
    )
    if len(_response) > 0:
        assert convert(_response, bool)

    return _balance
