# @version 0.2.4
# (c) Curve.Fi, 2020
# Deposit zap for the metapool
#
# Coins 0 .. N_COINS-2 are normal coins
# Coin N_COINS-1 is another pool token which has get_virtual_price()

from vyper.interfaces import ERC20


interface CurveMeta:
    def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]): nonpayable
    def base_pool() -> address: view

interface CurveBase:
    def add_liquidity(amounts: uint256[BASE_N_COINS], min_mint_amount: uint256): nonpayable
    def remove_liquidity(_amount: uint256, min_amounts: uint256[BASE_N_COINS]): nonpayable


N_COINS: constant(int128) = ___N_COINS___
BASE_N_COINS: constant(int128) = ___BASE_N_COINS___
N_ALL_COINS: constant(int128) = N_COINS + BASE_N_COINS - 1


pool: public(address)
token: public(address)
base_pool: public(address)


@external
def __init__(_pool: address, _token: address):
    self.pool = _pool
    self.token = _token
    self.base_pool = CurveMeta(_pool).base_pool()


@external
@nonreentrant('lock')
def add_liquidity(amounts: uint256[N_ALL_COINS], min_mint_amount: uint256):
    pass


@external
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, min_amounts: uint256[N_ALL_COINS]):
    pass


@external
@nonreentrant('lock')
def remove_liquidity_one_coin(_token_amount: uint256, i: int128, min_amount: uint256):
    pass


@view
@external
def calc_withdraw_one_coin(_token_amount: uint256, i: int128) -> uint256:
    return 0


@view
@external
def calc_token_amount(amounts: uint256[N_ALL_COINS], deposit: bool) -> uint256:
    return 0
