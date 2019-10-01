#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3.middleware import geth_poa_middleware
from tests import deploy_contract

# Deployment parameters
# PROVIDER_URI = expanduser('~/.ethereum/testnet/geth.ipc')
PROVIDER_URI = '/tmp/geth.ipc'
POA = True
N_COINS = 3
SWAP_DEPLOY_ADDRESS = '0xFD3DeCC0cF498bb9f54786cb65800599De505706'
COINS_DEPLOY_ADDRESS = '0x9CA6Eebc54efF56F1D0e844a41364c8aF2321520'


provider = Web3.IPCProvider(PROVIDER_URI)
w3 = Web3(provider)
if POA:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)


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
    pool_token.functions.set_minter(swap_contract.address).transact(
        {'from': SWAP_DEPLOY_ADDRESS})
    return swap_contract.address, pool_token.address


if __name__ == '__main__':
    print('coins = deploy_test_erc20() to deploy test coins')
    print('swap, token = deploy_swap(coins, A, fee) to deploy swap contract from the list')
    import IPython
    IPython.embed()
