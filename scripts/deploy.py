import json
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy as gas_strategy

from brownie import CurveToken, LiquidityGauge, StableSwap, accounts, web3


POOL_OWNER = "0x6e8f6D1DA6232d5E40b0B8758A0145D6C5123eB7"  # PoolProxy
MINTER = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"
DAI = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

AMP = 100
FEE = 4000000
ADMIN_FEE = 0

REQUIRED_CONFIRMATIONS = 3


def main(confs=REQUIRED_CONFIRMATIONS, apply_strategies=True):
    from .config_admin import INITIAL_ADMIN_KEY
    deployer = accounts.add(bytes.fromhex(INITIAL_ADMIN_KEY))

    if apply_strategies:
        web3.eth.setGasPriceStrategy(gas_strategy)
        web3.middleware_onion.add(middleware.time_based_cache_middleware)
        web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        web3.middleware_onion.add(middleware.simple_cache_middleware)

    token = CurveToken.deploy(
        "Curve.fi DAI/USDC/USDT",
        "3Crv",
        18,
        0,
        {'from': deployer, 'required_confs': confs}
    )

    swap = StableSwap.deploy(
        POOL_OWNER,
        [DAI, USDC, USDT],
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
