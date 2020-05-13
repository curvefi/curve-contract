#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3 import middleware
# from web3.gas_strategies.time_based import fast_gas_price_strategy
from web3.gas_strategies.time_based import medium_gas_price_strategy as gas_strategy
from tests.deploy import deploy_contract
import json

from deploy_config_renbtc import (
        COINS, SWAP_DEPLOY_ADDRESS,
        PRECISIONS, USE_LENDING)

# Deployment parameters
provider = Web3.IPCProvider('~/.ethereum/geth.ipc', timeout=10000, request_kwargs={'timeout': 10000})
POA = False
N_COINS = len(COINS)
GETH_PASSWORD = None

HELP = """swap, token = deploy_swap(A, fee) to deploy swap contract from the list
Try A=150, fee=0.0004
====================================================="""


w3 = Web3(provider)
w3.eth.setGasPriceStrategy(gas_strategy)

w3.middleware_onion.add(middleware.time_based_cache_middleware)
w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
w3.middleware_onion.add(middleware.simple_cache_middleware)

if POA:
    w3.middleware_onion.inject(middleware.geth_poa_middleware, layer=0)
_ = w3.eth.accounts


def deploy_swap(A, fee):
    if GETH_PASSWORD:
        w3.geth.personal.unlockAccount(w3.eth.accounts[0], GETH_PASSWORD)
    fee = int(fee * 10 ** 10)
    pool_token = deploy_contract(
        w3, 'ERC20.vy', SWAP_DEPLOY_ADDRESS, b'Curve.fi DAI/USDC/USDT/PAX', b'ypaxCrv', 18, 0)
    swap_contract = deploy_contract(
            w3, ['stableswap.vy', 'ERC20m.vy', 'cERC20.vy'], SWAP_DEPLOY_ADDRESS,
            COINS, pool_token.address, A, fee,
            replacements={
                '___N_COINS___': str(N_COINS),
                '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']',
                '___PRECISION_MUL___': '[' + ', '.join(
                    'convert(%s, uint256)' % (10 ** 18 // i) for i in PRECISIONS) + ']',
                '___USE_LENDING___': '[' + ', '.join(
                        str(i) for i in USE_LENDING) + ']',
            })
    txhash = pool_token.functions.set_minter(swap_contract.address).transact(
        {'from': SWAP_DEPLOY_ADDRESS})
    w3.eth.waitForTransactionReceipt(txhash, timeout=1000)

    abi = json.dumps(swap_contract.abi, indent=True)
    with open('swap.abi', 'w') as f:
        f.write(abi)
    print('---=== ABI ===---')
    print(abi)
    print('=================')
    print('Pool token:', pool_token.address)
    print('Swap contract:', swap_contract.address)

    return swap_contract, pool_token


if __name__ == '__main__':
    import IPython
    IPython.embed(header=HELP)
