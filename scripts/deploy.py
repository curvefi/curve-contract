import json
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy as gas_strategy

from brownie import CurveToken, LiquidityGauge, StableSwap, accounts, web3


POOL_OWNER = "0x6e8f6D1DA6232d5E40b0B8758A0145D6C5123eB7"  # PoolProxy
MINTER = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"
HBTC = "0x0316EB71485b0Ab14103307bf65a021042c6d380"
WBTC = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"

AMP = 100
FEE = 4000000
ADMIN_FEE = 0

REQUIRED_CONFIRMATIONS = 1


def main(confs=REQUIRED_CONFIRMATIONS, apply_strategies=True):
    deployer = accounts.add()  # set me

    if apply_strategies:
        web3.eth.setGasPriceStrategy(gas_strategy)
        web3.middleware_onion.add(middleware.time_based_cache_middleware)
        web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        web3.middleware_onion.add(middleware.simple_cache_middleware)

    token = CurveToken.deploy(
        "Curve.fi hBTC/wBTC",
        "hCRV",
        18,
        0,
        {'from': deployer, 'required_confs': confs}
    )

    swap = StableSwap.deploy(
        POOL_OWNER,
        [HBTC, WBTC],
        token,
        AMP,
        FEE,
        ADMIN_FEE,
        {'from': deployer, 'required_confs': confs}
    )

    with open('StableSwap.abi', 'w') as fp:
        json.dump(swap.abi, fp, indent=True)

    LiquidityGauge.deploy(token, MINTER, {'from': deployer, 'required_confs': confs})

    token.set_minter(swap, {'from': deployer, 'required_confs': confs})
