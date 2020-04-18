#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy
from tests.deploy import deploy_contract
from deploy_config_susd import (
        SWAP_DEPLOY_ADDRESS, Y_COINS, UNDERLYING_COINS, Y_ZAP_ADDRESS,
        PRECISIONS, Y_POOL_ADDRESS, SUSD_SWAP_ADDRESS, SUSD_TOKEN_ADDRESS,
        PRECISIONS_Y)
import json

# Deployment parameters
provider = Web3.IPCProvider('~/.ethereum/geth.ipc', timeout=10000, request_kwargs={'timeout': 10000})
POA = False
N_COINS = len(Y_COINS)
GETH_PASSWORD = None

w3 = Web3(provider)
w3.eth.setGasPriceStrategy(fast_gas_price_strategy)

w3.middleware_onion.add(middleware.time_based_cache_middleware)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

if POA:
    w3.middleware_onion.inject(middleware.geth_poa_middleware, layer=0)
_ = w3.eth.accounts


def deploy_zap():
    if GETH_PASSWORD:
        w3.geth.personal.unlockAccount(w3.eth.accounts[0], GETH_PASSWORD)
    deposit_contract = deploy_contract(
            w3, ['deposit.vy', 'yERC20.vy'], SWAP_DEPLOY_ADDRESS,
            Y_COINS,
            [UNDERLYING_COINS[0], Y_POOL_ADDRESS],
            SUSD_SWAP_ADDRESS, SUSD_TOKEN_ADDRESS, Y_ZAP_ADDRESS,
            replacements={
                '___PRECISION_MUL___': '[' + ', '.join(
                    'convert(%s, uint256)' % i for i in PRECISIONS[:-1] + PRECISIONS_Y) + ']',
            })
    abi = json.dumps(deposit_contract.abi, indent=True)
    with open('deposit.abi', 'w') as f:
        f.write(abi)
    print('Deposit:', deposit_contract.address)

    return deposit_contract


if __name__ == '__main__':
    deploy_zap()
