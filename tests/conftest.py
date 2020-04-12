import pytest
import json
from eth_tester import EthereumTester, PyEVMBackend
from web3 import Web3
from os.path import realpath, dirname, join
from .deploy import deploy_contract

CONTRACT_PATH = join(dirname(dirname(realpath(__file__))), 'vyper')
N_COINS = 2
UP = [18, 18]
UU = [10 ** p for p in UP]
UPY = [18, 6, 6, 18]
UUY = [10 ** p for p in UPY]
c_rates = [5 * UU[0], UU[1]]
c_rates_y = [5 * UUY[0], UUY[1], 3 * UUY[2], UUY[3]]
use_lending = [True, False]
use_curved = [False, True]
tethered = [False, False]
PRECISIONS = [10 ** 18 // u for u in UU]
PRECISIONS_Y = [10 ** 18 // u for u in UUY]
MAX_UINT = 2 ** 256 - 1


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
def crvERC20s(w3, coins):
    return [deploy_contract(
                w3, 'fake_crverc20.vy', w3.eth.accounts[0],
                c_rates[i])
            for i in range(N_COINS)]


@pytest.fixture
def pool_token(w3):
    return deploy_contract(w3, 'ERC20.vy', w3.eth.accounts[0],
                           b'Stableswap', b'STBL', 18, 0)


@pytest.fixture
def yerc20s(w3, coins):
    ccoins = [deploy_contract(
                w3, 'fake_yerc20.vy', w3.eth.accounts[0],
                b'C-Coin ' + str(i).encode(), b'c' + str(i).encode(),
                18, 0, coins[i].address, c_rates[i])
              for i in range(N_COINS)]
    for t, c, u in zip(coins, ccoins, UU):
        t.functions.transfer(c.address, 10 ** 11 * u)\
                .transact({'from': w3.eth.accounts[0]})
    for i, l in enumerate(use_lending):
        if not l:
            ccoins[i] = coins[i]
    return ccoins


@pytest.fixture
def coins_y(w3):
    return [deploy_contract(
                w3, 'ERC20.vy', w3.eth.accounts[0],
                b'Coin ' + str(i).encode(), str(i).encode(), UPY[i], 10 ** 12)
            for i in range(len(UPY))]


@pytest.fixture
def yerc20s_y(w3, coins_y):
    ccoins = [deploy_contract(
                w3, 'fake_yerc20.vy', w3.eth.accounts[0],
                b'C-Coin ' + str(i).encode(), b'c' + str(i).encode(),
                18, 0, coins_y[i].address, c_rates_y[i])
              for i in range(len(UPY))]
    for t, c, u in zip(coins_y, ccoins, UUY):
        t.functions.transfer(c.address, 10 ** 11 * u)\
                .transact({'from': w3.eth.accounts[0]})
    for i, l in enumerate(use_lending):
        if not l:
            ccoins[i] = coins[i]
    return ccoins


@pytest.fixture
def pool_token_y(w3):
    return deploy_contract(w3, 'ERC20.vy', w3.eth.accounts[0],
                           b'Stableswap', b'STBL', 18, 0)


@pytest.fixture(scope='function')
def swap(w3, coins, yerc20s, crvERC20s, pool_token):
    swap_contract = deploy_contract(
            w3, ['stableswap.vy', 'ERC20m.vy', 'yERC20.vy'], w3.eth.accounts[1],
            [c.address for c in yerc20s], [c.address for c in coins],
            [c.address for c in crvERC20s], pool_token.address, 360 * 2, 10 ** 7,
            replacements={
                '___N_COINS___': str(N_COINS),
                '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']',
                '___PRECISION_MUL___': '[' + ', '.join(
                    'convert(%s, uint256)' % i for i in PRECISIONS) + ']',
                '___USE_LENDING___': '[' + ', '.join(
                        str(i) for i in use_lending) + ']',
                '___USE_CURVED___': '[' + ', '.join(
                        str(i) for i in use_curved) + ']',
                '___TETHERED___': '[' + ', '.join(
                        str(i) for i in tethered) + ']',
            })
    pool_token.functions.set_minter(swap_contract.address).transact()
    with open(join(CONTRACT_PATH, 'stableswap.abi'), 'w') as f:
        json.dump(swap_contract.abi, f, indent=True)
    return swap_contract


def approx(a, b, precision=1e-10):
    return 2 * abs(a - b) / (a + b) <= precision
