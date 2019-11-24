import pytest
import json
from eth_tester import EthereumTester, PyEVMBackend
from web3 import Web3
from os.path import realpath, dirname, join
from .deploy import deploy_contract

CONTRACT_PATH = join(dirname(dirname(realpath(__file__))), 'vyper')
N_COINS = 3
PRECISIONS = [10 ** 18, 10 ** 6, 10 ** 6]


@pytest.fixture
def tester():
    genesis_params = PyEVMBackend._generate_genesis_params(overrides={'gas_limit': 7 * 10 ** 6})
    pyevm_backend = PyEVMBackend(genesis_parameters=genesis_params)
    pyevm_backend.reset_to_genesis(genesis_params=genesis_params, num_accounts=10)
    return EthereumTester(backend=pyevm_backend, auto_mine_transactions=True)


@pytest.fixture
def w3(tester):
    w3 = Web3(Web3.EthereumTesterProvider(tester))
    w3.eth.setGasPriceStrategy(lambda web3, params: 0)
    w3.eth.defaultAccount = w3.eth.accounts[0]
    return w3


@pytest.fixture
def coins(w3):
    return [deploy_contract(
                w3, 'ERC20.vy', w3.eth.accounts[0],
                b'Coin ' + str(i).encode(), str(i).encode(), 18, 10 ** 9)
            for i in range(N_COINS)]


@pytest.fixture
def pool_token(w3):
    return deploy_contract(w3, 'ERC20.vy', w3.eth.accounts[0],
                           b'Stableswap', b'STBL', 18, 0)


@pytest.fixture(scope='function')
def swap(w3, coins, pool_token):
    swap_contract = deploy_contract(
            w3, ['stableswap.vy', 'ERC20m.vy'], w3.eth.accounts[1],
            [c.address for c in coins], pool_token.address, 360 * 2, 10 ** 7)
    pool_token.functions.set_minter(swap_contract.address).transact()
    with open(join(CONTRACT_PATH, 'stableswap.abi'), 'w') as f:
        json.dump(swap_contract.abi, f, indent=True)
    return swap_contract
