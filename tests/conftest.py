import pytest
from eth_tester import EthereumTester, PyEVMBackend
from web3 import Web3
from os.path import realpath, dirname, join
from vyper import compile_code
from web3.contract import ConciseContract

CONTRACT_PATH = join(dirname(dirname(realpath(__file__))), 'vyper')


@pytest.fixture
def tester():
    return EthereumTester(backend=PyEVMBackend(), auto_mine_transactions=True)


@pytest.fixture
def w3(tester):
    w3 = Web3(Web3.EthereumTesterProvider(tester))
    w3.eth.setGasPriceStrategy(lambda web3, params: 0)
    w3.eth.defaultAccount = w3.eth.accounts[0]
    return w3


def deploy_contract(w3, filename, account, *args):
    with open(join(CONTRACT_PATH, filename)) as f:
        source = f.read()
    code = compile_code(source, ['bytecode', 'abi'])
    deploy = w3.eth.contract(abi=code['abi'],
                             bytecode=code['bytecode'])
    tx_hash = deploy.constructor(*args).transact({'from': account})
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return ConciseContract(w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi))


@pytest.fixture
def coin_a(w3):
    return deploy_contract(
            w3, 'ERC20.vy', w3.eth.accounts[1],
            b'Coin A', b'A', 18, 10 ** 9)


@pytest.fixture
def coin_b(w3):
    return deploy_contract(
            w3, 'ERC20.vy', w3.eth.accounts[1],
            b'Coin B', b'B', 18, 10 ** 9)


@pytest.fixture
def swap(w3, coin_a, coin_b):
    return deploy_contract(
            w3, 'stableswap.vy', w3.eth.accounts[1],
            coin_a.address, coin_b.address, 100, 0.001)
