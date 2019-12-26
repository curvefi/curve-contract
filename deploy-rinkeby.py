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
UNDERLYING_COINS = ['0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa', '0x4DBCdF9B62e891a7cec5A2568C3F4FAF9E8Abe2b']
C_COINS = ['0x6D7F0754FFeb405d23C51CE938289d4835bE3b14', '0x5B281A6DdA0B271e91ae35DE655Ad301C976edb1']
PRECISIONS = [10 ** 18, 10 ** 6]
N_COINS = len(C_COINS)
SWAP_DEPLOY_ADDRESS = '0x8E082A9f19f62C21e8b6bB542ca9F57148c64131'  # password - "test"

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
                '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']',
                '___PRECISION_MUL___': '[' + ', '.join([
                    'PRECISION / convert(%s, uint256)' % i
                    for i in PRECISIONS]) + ']'
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
