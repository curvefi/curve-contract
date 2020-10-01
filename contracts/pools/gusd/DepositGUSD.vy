# @version 0.2.5
# (c) Curve.Fi, 2020
# Deposit zap for the metapool
#
# Coins 0 .. N_COINS-2 are normal coins
# Coin N_COINS-1 is another pool token which has get_virtual_price()

from vyper.interfaces import ERC20


interface CurveMeta:
    def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]): nonpayable
    def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_amount: uint256): nonpayable
    def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256: view
    def calc_token_amount(amounts: uint256[N_COINS], deposit: bool) -> uint256: view
    def base_pool() -> address: view
    def coins(i: uint256) -> address: view

interface CurveBase:
    def add_liquidity(amounts: uint256[BASE_N_COINS], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[BASE_N_COINS]): nonpayable
    def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_amount: uint256): nonpayable
    def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256: view
    def calc_token_amount(amounts: uint256[BASE_N_COINS], deposit: bool) -> uint256: view
    def coins(i: uint256) -> address: view


N_COINS: constant(int128) = 2
MAX_COIN: constant(int128) = N_COINS-1
BASE_N_COINS: constant(int128) = 3
N_ALL_COINS: constant(int128) = N_COINS + BASE_N_COINS - 1
#
# An asset shich may have a transfer fee (USDT)
FEE_ASSET: constant(address) = 0xdAC17F958D2ee523a2206206994597C13D831ec7


pool: public(address)
token: public(address)
base_pool: public(address)

coins: public(address[N_COINS])
base_coins: public(address[BASE_N_COINS])


@external
def __init__(_pool: address, _token: address):
    self.pool = _pool
    self.token = _token
    _base_pool: address = CurveMeta(_pool).base_pool()
    self.base_pool = _base_pool

    for i in range(N_COINS):
        coin: address = CurveMeta(_pool).coins(convert(i, uint256))
        self.coins[i] = coin
        # approve coins for infinite transfers
        _response: Bytes[32] = raw_call(
            coin,
            concat(
                method_id("approve(address,uint256)"),
                convert(_pool, bytes32),
                convert(MAX_UINT256, bytes32),
            ),
            max_outsize=32,
        )
        if len(_response) > 0:
            assert convert(_response, bool)

    for i in range(BASE_N_COINS):
        coin: address = CurveBase(_base_pool).coins(convert(i, uint256))
        self.base_coins[i] = coin
        # approve underlying coins for infinite transfers
        _response: Bytes[32] = raw_call(
            coin,
            concat(
                method_id("approve(address,uint256)"),
                convert(_base_pool, bytes32),
                convert(MAX_UINT256, bytes32),
            ),
            max_outsize=32,
        )
        if len(_response) > 0:
            assert convert(_response, bool)


@external
@nonreentrant('lock')
def add_liquidity(amounts: uint256[N_ALL_COINS], min_mint_amount: uint256) -> uint256:
    meta_amounts: uint256[N_COINS] = empty(uint256[N_COINS])
    base_amounts: uint256[BASE_N_COINS] = empty(uint256[BASE_N_COINS])
    deposit_base: bool = False

    # Transfer all coins in
    for i in range(N_ALL_COINS):
        amount: uint256 = amounts[i]
        if amount == 0:
            continue
        coin: address = ZERO_ADDRESS
        if i < MAX_COIN:
            coin = self.coins[i]
            meta_amounts[i] = amount
        else:
            x: int128 = i - MAX_COIN
            coin = self.base_coins[x]
            base_amounts[x] = amount
            deposit_base = True
        # "safeTransferFrom" which works for ERC20s which return bool or not
        _response: Bytes[32] = raw_call(
            coin,
            concat(
                method_id("transferFrom(address,address,uint256)"),
                convert(msg.sender, bytes32),
                convert(self, bytes32),
                convert(amount, bytes32),
            ),
            max_outsize=32,
        )  # dev: failed transfer
        if len(_response) > 0:
            assert convert(_response, bool)  # dev: failed transfer
        # end "safeTransferFrom"
        # Handle potential Tether fees
        if coin == FEE_ASSET:
            amount = ERC20(FEE_ASSET).balanceOf(self)
            if i < MAX_COIN:
                meta_amounts[i] = amount
            else:
                base_amounts[i - MAX_COIN] = amount

    # Deposit to the base pool
    if deposit_base:
        CurveBase(self.base_pool).add_liquidity(base_amounts, 0)
        meta_amounts[MAX_COIN] = ERC20(self.coins[MAX_COIN]).balanceOf(self)

    # Deposit to the meta pool
    CurveMeta(self.pool).add_liquidity(meta_amounts, min_mint_amount)

    # Transfer meta token back
    _lp_token: address = self.token
    _lp_amount: uint256 = ERC20(_lp_token).balanceOf(self)
    assert ERC20(_lp_token).transfer(msg.sender, _lp_amount)

    return _lp_amount


@external
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, min_amounts: uint256[N_ALL_COINS]) -> uint256[N_ALL_COINS]:
    _token: address = self.token
    assert ERC20(_token).transferFrom(msg.sender, self, _amount)

    min_amounts_meta: uint256[N_COINS] = empty(uint256[N_COINS])
    min_amounts_base: uint256[BASE_N_COINS] = empty(uint256[BASE_N_COINS])
    amounts: uint256[N_ALL_COINS] = empty(uint256[N_ALL_COINS])

    # Withdraw from meta
    for i in range(MAX_COIN):
        min_amounts_meta[i] = min_amounts[i]
    CurveMeta(self.pool).remove_liquidity(_amount, min_amounts_meta)

    # Withdraw from base
    _base_amount: uint256 = ERC20(self.coins[1]).balanceOf(self)
    for i in range(BASE_N_COINS):
        min_amounts_base[i] = min_amounts[MAX_COIN+i]
    CurveBase(self.base_pool).remove_liquidity(_base_amount, min_amounts_base)

    # Transfer all coins out
    for i in range(N_ALL_COINS):
        coin: address = ZERO_ADDRESS
        if i < MAX_COIN:
            coin = self.coins[i]
        else:
            coin = self.base_coins[i - MAX_COIN]
        amounts[i] = ERC20(coin).balanceOf(self)
        # "safeTransfer" which works for ERC20s which return bool or not
        _response: Bytes[32] = raw_call(
            coin,
            concat(
                method_id("transfer(address,uint256)"),
                convert(msg.sender, bytes32),
                convert(amounts[i], bytes32),
            ),
            max_outsize=32,
        )  # dev: failed transfer
        if len(_response) > 0:
            assert convert(_response, bool)  # dev: failed transfer
        # end "safeTransfer"

    return amounts


@external
@nonreentrant('lock')
def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_amount: uint256) -> uint256:
    _token: address = self.token
    assert ERC20(_token).transferFrom(msg.sender, self, _token_amount)

    coin: address = ZERO_ADDRESS
    if i < MAX_COIN:
        coin = self.coins[i]
        # Withdraw a metapool coin
        CurveMeta(self.pool).remove_liquidity_one_coin(_token_amount, i, min_amount)
    else:
        coin = self.base_coins[i - MAX_COIN]
        # Withdraw a base pool coin
        CurveMeta(self.pool).remove_liquidity_one_coin(_token_amount, MAX_COIN, 0)
        CurveBase(self.base_pool).remove_liquidity_one_coin(
            ERC20(self.coins[MAX_COIN]).balanceOf(self), i-MAX_COIN, min_amount
        )

    # Tranfer the coin out
    coin_amount: uint256 = ERC20(coin).balanceOf(self)
    # "safeTransfer" which works for ERC20s which return bool or not
    _response: Bytes[32] = raw_call(
        coin,
        concat(
            method_id("transfer(address,uint256)"),
            convert(msg.sender, bytes32),
            convert(coin_amount, bytes32),
        ),
        max_outsize=32,
    )  # dev: failed transfer
    if len(_response) > 0:
        assert convert(_response, bool)  # dev: failed transfer
    # end "safeTransfer"

    return coin_amount


@view
@external
def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256:
    if i < MAX_COIN:
        return CurveMeta(self.pool).calc_withdraw_one_coin(_token_amount, i)
    else:
        _base_tokens: uint256 = CurveMeta(self.pool).calc_withdraw_one_coin(_token_amount, MAX_COIN)
        return CurveBase(self.base_pool).calc_withdraw_one_coin(_base_tokens, i-MAX_COIN)


@view
@external
def calc_token_amount(amounts: uint256[N_ALL_COINS], deposit: bool) -> uint256:
    meta_amounts: uint256[N_COINS] = empty(uint256[N_COINS])
    base_amounts: uint256[BASE_N_COINS] = empty(uint256[BASE_N_COINS])

    for i in range(MAX_COIN):
        meta_amounts[i] = amounts[i]

    for i in range(BASE_N_COINS):
        base_amounts[i] = amounts[i + MAX_COIN]

    _base_tokens: uint256 = CurveBase(self.base_pool).calc_token_amount(base_amounts, deposit)
    meta_amounts[MAX_COIN] = _base_tokens

    return CurveMeta(self.pool).calc_token_amount(meta_amounts, deposit)
