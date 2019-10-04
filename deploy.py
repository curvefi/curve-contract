#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3.middleware import geth_poa_middleware
from tests.deploy import deploy_contract
import json

# Deployment parameters
provider = Web3.IPCProvider('../geth/geth.ipc')
# provider = Web3.HTTPProvider('http://127.0.0.1:8545')
POA = True
FUND_DEV = True
N_COINS = 3
SWAP_DEPLOY_ADDRESS = '0x81852cf89dF0FE34716129f1a3f9F065Cf9f8DeC'
COINS_DEPLOY_ADDRESS = '0xC6C362126eB202b8c416266D0AF929317F4d663a'
TOKENS_FUND_ADDRS = ['0x08A9bC278d07FF55A344e9ED57cB57594e9ea9dF',
                     '0x07Aae93f2182e43245Fd35d709d9F8F69aaE4EDD']

HELP = """coins = deploy_test_erc20() to deploy test coins
swap, token = deploy_swap(coins, A, fee) to deploy swap contract from the list
transfer(coins) to fund accounts
====================================================="""


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
                )
            for i in range(N_COINS)]


def deploy_swap(coins, A, fee):
    if not isinstance(coins[0], str):
        coins = [c.address for c in coins]
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

    abi = json.dumps(swap_contract.abi, indent=True)
    with open('swap.abi', 'w') as f:
        f.write(abi)
    print('---=== ABI ===---')
    print(abi)
    print('=================')

    return swap_contract, pool_token


def transfer_erc20(coins):
    for c in coins:
        for addr in TOKENS_FUND_ADDRS:
            print(f'Transferring {c.address} to {addr}')
            txhash = c.functions.transfer(addr, 10000 * 10 ** 18).transact({'from': COINS_DEPLOY_ADDRESS})
            w3.eth.waitForTransactionReceipt(txhash)


if __name__ == '__main__':
    import IPython
    IPython.embed(header=HELP)
