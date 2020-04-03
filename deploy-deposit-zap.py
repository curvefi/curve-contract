#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy
from tests.deploy import deploy_contract
from deploy_config_compound import (
        SWAP_DEPLOY_ADDRESS, C_COINS, UNDERLYING_COINS, USE_LENDING, TETHERED,
        PRECISIONS, SWAP_ADDRESS, TOKEN_ADDERESS)
import json

# Deployment parameters
provider = Web3.IPCProvider('~/.ethereum/geth.ipc', timeout=10000, request_kwargs={'timeout': 10000})
POA = False
# DAI, USDC
N_COINS = len(C_COINS)
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
            w3, ['deposit.vy', 'cERC20.vy'], SWAP_DEPLOY_ADDRESS,
            C_COINS, UNDERLYING_COINS, SWAP_ADDRESS, TOKEN_ADDERESS,
            replacements={
                '___N_COINS___': str(N_COINS),
                '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']',
                '___PRECISION_MUL___': '[' + ', '.join(
                    'convert(%s, uint256)' % (10 ** 18 // i) for i in PRECISIONS) + ']',
                '___USE_LENDING___': '[' + ', '.join(
                        str(i) for i in USE_LENDING) + ']',
                '___TETHERED___': '[' + ', '.join(
                        str(i) for i in TETHERED) + ']',
            })

    abi = json.dumps(deposit_contract.abi, indent=True)
    with open('deposit.abi', 'w') as f:
        f.write(abi)
    print('Deposit:', deposit_contract.address)

    return deposit_contract


if __name__ == '__main__':
    deploy_zap()
