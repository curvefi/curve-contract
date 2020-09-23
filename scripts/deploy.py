import json
import requests

from brownie import CurveTokenV2, StableSwapBase, StableSwapYLend, DepositYLend, accounts

# modify this import if you wish to deploy a different liquidity gauge
from brownie import LiquidityGauge as LiquidityGauge

# set a throwaway admin account here
DEPLOYER = accounts.add()

REQUIRED_CONFIRMATIONS = 1

# deployment settings
LP_TOKEN_NAME = "Curve.fi xx/xx/xx"
LP_TOKEN_SYMBOL = "[x]CRV"
WRAPPED_COINS = []
UNDERLYING_COINS = [
    # "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
    # "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
    # "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
]
AMP = 100
FEE = 4000000           # 0.04%
ADMIN_FEE = 5000000000  # 50% of FEE

POOL_OWNER = "0x6e8f6D1DA6232d5E40b0B8758A0145D6C5123eB7"  # PoolProxy
MINTER = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"


def base(confs=REQUIRED_CONFIRMATIONS):
    _deploy(confs, None, None)


def ylend(confs=REQUIRED_CONFIRMATIONS):
    _deploy(confs, StableSwapYLend, DepositYLend)


def _gas_price():
    data = requests.get("https://www.gasnow.org/api/v3/gas/price").json()
    # change `fast` to `rapid` if you're in a hurry
    return data['data']['fast'] + 10**9


def _deploy(confs, lending_contract, deposit_contract):

    token = CurveTokenV2.deploy(
        LP_TOKEN_NAME,
        LP_TOKEN_SYMBOL,
        18,
        0,
        {'from': DEPLOYER, 'required_confs': confs, 'gas_price': _gas_price()}
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
            {'from': DEPLOYER, 'required_confs': confs, 'gas_price': _gas_price()}
        )
        deposit_contract.deploy(
            WRAPPED_COINS,
            UNDERLYING_COINS,
            swap,
            token,
            {'from': DEPLOYER, 'required_confs': confs, 'gas_price': _gas_price()}
        )

    else:
        swap = StableSwapBase.deploy(
            POOL_OWNER,
            UNDERLYING_COINS,
            token,
            AMP,
            FEE,
            ADMIN_FEE,
            {'from': DEPLOYER, 'required_confs': confs, 'gas_price': _gas_price()}
        )

    with open('StableSwap.abi', 'w') as fp:
        json.dump(swap.abi, fp, indent=True)

    token.set_minter(
        swap,
        {'from': DEPLOYER, 'required_confs': confs, 'gas_price': _gas_price()}
    )

    LiquidityGauge.deploy(
        token,
        MINTER,
        {'from': DEPLOYER, 'required_confs': confs, 'gas_price': _gas_price()}
    )
