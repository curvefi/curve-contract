import json
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy as gas_strategy

from brownie import CurveToken, StableSwapBase, StableSwapYLend, accounts, web3

# modify this import if you wish to deploy a different liquidity gauge
from brownie import LiquidityGauge as LiquidityGauge

# set a throwaway admin account here
DEPLOYER = accounts.add()

REQUIRED_CONFIRMATIONS = 1

# deployment settings
LP_TOKEN_NAME = ""
LP_TOKEN_SYMBOL = ""
WRAPPED_COINS = []
UNDERLYING_COINS = []
AMP = 100
FEE = 4000000
ADMIN_FEE = 0

POOL_OWNER = "0x6e8f6D1DA6232d5E40b0B8758A0145D6C5123eB7"  # PoolProxy
MINTER = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"


def base(confs=REQUIRED_CONFIRMATIONS, apply_strategies=True):
    _deploy(confs, apply_strategies, None)


def ylend(confs=REQUIRED_CONFIRMATIONS, apply_strategies=True):
    _deploy(confs, apply_strategies, StableSwapYLend)


def _deploy(confs, apply_strategies, lending_contract):

    if apply_strategies:
        web3.eth.setGasPriceStrategy(gas_strategy)
        web3.middleware_onion.add(middleware.time_based_cache_middleware)
        web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        web3.middleware_onion.add(middleware.simple_cache_middleware)

    token = CurveToken.deploy(
        LP_TOKEN_NAME,
        LP_TOKEN_SYMBOL,
        18,
        0,
        {'from': DEPLOYER, 'required_confs': confs}
    )

    if lending_contract is not None:
        swap = lending_contract.deploy(
            POOL_OWNER,
            WRAPPED_COINS,
            UNDERLYING_COINS,
            token,
            AMP,
            FEE,
            ADMIN_FEE,
            {'from': DEPLOYER, 'required_confs': confs}
        )
    else:
        swap = StableSwapBase.deploy(
            POOL_OWNER,
            UNDERLYING_COINS,
            token,
            AMP,
            FEE,
            ADMIN_FEE,
            {'from': DEPLOYER, 'required_confs': confs}
        )

    with open('StableSwap.abi', 'w') as fp:
        json.dump(swap.abi, fp, indent=True)

    token.set_minter(swap, {'from': DEPLOYER, 'required_confs': confs})

    LiquidityGauge.deploy(token, MINTER, {'from': DEPLOYER, 'required_confs': confs})
