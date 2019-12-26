import pytest
import json
from eth_tester import EthereumTester, PyEVMBackend
from web3 import Web3
from os.path import realpath, dirname, join
from .deploy import deploy_contract

CONTRACT_PATH = join(dirname(dirname(realpath(__file__))), 'vyper')
N_COINS = 3
UP = [18, 6, 6]
UU = [10 ** p for p in UP]
c_rates = [5 * UU[0], UU[1], 20 * UU[2]]
PRECISIONS = [10 ** 18 // u for u in UU]


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
                b'Coin ' + str(i).encode(), str(i).encode(), UP[i], 10 ** 12)
            for i in range(N_COINS)]


@pytest.fixture
def pool_token(w3):
    return deploy_contract(w3, 'ERC20.vy', w3.eth.accounts[0],
                           b'Stableswap', b'STBL', 18, 0)


@pytest.fixture
def cerc20s(w3, coins):
    ccoins = [deploy_contract(
                w3, 'fake_cerc20.vy', w3.eth.accounts[0],
                b'C-Coin ' + str(i).encode(), b'c' + str(i).encode(),
                18, 0, coins[i].address, c_rates[i])
              for i in range(N_COINS)]
    for t, c, u in zip(coins, ccoins, UU):
        t.functions.transfer(c.address, 10 ** 11 * u)\
                .transact({'from': w3.eth.accounts[0]})
    return ccoins


@pytest.fixture(scope='function')
def swap(w3, coins, cerc20s, pool_token):
    swap_contract = deploy_contract(
            w3, ['stableswap.vy', 'ERC20m.vy', 'cERC20.vy'], w3.eth.accounts[1],
            [c.address for c in cerc20s], [c.address for c in coins],
            pool_token.address, 360 * 2, 10 ** 7,
            replacements={
                '___N_COINS___': str(N_COINS),
                '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']',
                '___PRECISION_MUL___': '[' + ', '.join([
                    'PRECISION / convert(%s, uint256)' % i
                    for i in (10 ** 18, 10 ** 6, 10 ** 6)]) + ']'
            })
    pool_token.functions.set_minter(swap_contract.address).transact()
    with open(join(CONTRACT_PATH, 'stableswap.abi'), 'w') as f:
        json.dump(swap_contract.abi, f, indent=True)
    return swap_contract
