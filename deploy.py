#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3.middleware import geth_poa_middleware
from tests.deploy import deploy_contract
import json

# Deployment parameters
# PROVIDER_URI = expanduser('~/.ethereum/testnet/geth.ipc')
PROVIDER_URI = '/tmp/geth.ipc'
POA = True
FUND_DEV = True
N_COINS = 3
SWAP_DEPLOY_ADDRESS = '0xFD3DeCC0cF498bb9f54786cb65800599De505706'
COINS_DEPLOY_ADDRESS = '0x9CA6Eebc54efF56F1D0e844a41364c8aF2321520'

HELP = """coins = deploy_test_erc20() to deploy test coins
swap, token = deploy_swap(coins, A, fee) to deploy swap contract from the list
====================================================="""


provider = Web3.IPCProvider(PROVIDER_URI)
w3 = Web3(provider)
if POA:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
if FUND_DEV:
    txhash = w3.eth.sendTransaction({
        'from': w3.eth.accounts[0],
        'to': SWAP_DEPLOY_ADDRESS,
        'value': 10 ** 19})
    w3.eth.waitForTransactionReceipt(txhash)
    txhash = w3.eth.sendTransaction({
        'from': w3.eth.accounts[0],
        'to': COINS_DEPLOY_ADDRESS,
        'value': 10 ** 19})
    w3.eth.waitForTransactionReceipt(txhash)


def deploy_test_erc20():
    return [deploy_contract(
                w3, 'ERC20.vy', COINS_DEPLOY_ADDRESS,
                b'Coin ' + str(i).encode(), str(i).encode(), 18, 10 ** 9
                ).address
            for i in range(N_COINS)]


def deploy_swap(coins, A, fee):
    A = A * 2
    fee = int(fee * 10 ** 10)
    pool_token = deploy_contract(
        w3, 'ERC20.vy', SWAP_DEPLOY_ADDRESS, b'Stableswap', b'STBL', 18, 0)
    swap_contract = deploy_contract(
            w3, ['stableswap.vy', 'ERC20m.vy'], SWAP_DEPLOY_ADDRESS,
            coins, pool_token.address, A, fee)
    txhash = pool_token.functions.set_minter(swap_contract.address).transact(
        {'from': SWAP_DEPLOY_ADDRESS})
    w3.eth.waitForTransactionReceipt(txhash)
    print('---=== ABI ===---')
    print(json.dumps(swap_contract.abi, indent=True))
    print('=================')
    return swap_contract, pool_token


if __name__ == '__main__':
    import IPython
    IPython.embed(header=HELP)
