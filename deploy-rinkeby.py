#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3.middleware import geth_poa_middleware
from tests.deploy import deploy_contract
import json

# Deployment parameters
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
POA = True
# DAI, USDC
UNDERLYING_COINS = ['0x4F96Fe3b7A6Cf9725f59d353F723c1bDb64CA6Aa', '0x75B0622Cec14130172EaE9Cf166B92E5C112FaFF']
C_COINS = ['0xe7bc397DBd069fC7d0109C0636d06888bb50668c', '0xcfC9bB230F00bFFDB560fCe2428b4E05F3442E35']
N_COINS = len(C_COINS)
SWAP_DEPLOY_ADDRESS = '0x6A8c58940dDF516e96635188AaCCBD43E9A77829'

HELP = """swap, token = deploy_swap(coins, A, fee) to deploy swap contract from the list
====================================================="""


w3 = Web3(provider)
if POA:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)


def deploy_swap(A, fee):
    A = A * 2
    fee = int(fee * 10 ** 10)
    pool_token = deploy_contract(
        w3, 'ERC20.vy', SWAP_DEPLOY_ADDRESS, b'Stableswap', b'STBL', 18, 0)
    swap_contract = deploy_contract(
            w3, ['stableswap.vy', 'ERC20m.vy'], SWAP_DEPLOY_ADDRESS,
            C_COINS, UNDERLYING_COINS, pool_token.address, A, fee,
            replacements={
                '___N_COINS___': str(N_COINS),
                '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']'
            })
    txhash = pool_token.functions.set_minter(swap_contract.address).transact(
        {'from': SWAP_DEPLOY_ADDRESS})
    w3.eth.waitForTransactionReceipt(txhash)

    abi = json.dumps(swap_contract.abi, indent=True)
    with open('swap.abi', 'w') as f:
        f.write(abi)
    print('---=== ABI ===---')
    print(abi)
    print('=================')

    return swap_contract, pool_token


if __name__ == '__main__':
    import IPython
    IPython.embed(header=HELP)
