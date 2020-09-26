import pytest
import requests

from brownie.convert import to_address

from conftest import WRAPPED_COIN_METHODS
from scripts.utils import right_pad, pack_values

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module")
def MintableTestToken(Contract, accounts, web3, pool_data):

    class _MintableTestToken(Contract):

        _holders = {}

        def __init__(self, address):
            super().__init__(address)

            # standardize mint / rate methods
            if 'wrapped_contract' in pool_data:
                fn_names = WRAPPED_COIN_METHODS[pool_data['wrapped_contract']]
                for target, attr in fn_names.items():
                    if hasattr(self, attr):
                        setattr(self, target, getattr(self, attr))

            # get top token holder addresses
            address = self.address
            if address not in self._holders:
                holders = requests.get(
                    f"https://api.ethplorer.io/getTopTokenHolders/{address}",
                    params={'apiKey': "freekey", 'limit': 50},
                ).json()
                self._holders[address] = [to_address(i['address']) for i in holders['holders']]

        def _mint_for_testing(self, target, amount, tx=None):
            for address in self._holders[self.address].copy():
                if address == self.address:
                    # don't claim from the treasury - that could cause wierdness
                    continue

                balance = self.balanceOf(address)
                if amount > balance:
                    self.transfer(target, balance, {'from': address})
                    amount -= balance
                else:
                    self.transfer(target, amount, {'from': address})
                    return

            raise ValueError("Insufficient tokens available to mint")

    yield _MintableTestToken


@pytest.fixture(scope="module")
def wrapped_coins(MintableTestToken, project, alice, pool_data, underlying_coins, is_forked):
    coins = []

    if not pool_data.get("wrapped_contract"):
        yield underlying_coins

    elif is_forked:
        for i, coin_data in enumerate(pool_data['coins']):
            if not coin_data['wrapped']:
                coins.append(underlying_coins[i])
            else:
                coins.append(MintableTestToken(coin_data['wrapped_address']))
        yield coins

    else:
        fn_names = WRAPPED_COIN_METHODS[pool_data['wrapped_contract']]
        deployer = getattr(project, pool_data['wrapped_contract'])
        for i, coin_data in enumerate(pool_data['coins']):
            underlying = underlying_coins[i]
            if not coin_data['wrapped']:
                coins.append(underlying)
            else:
                decimals = coin_data['wrapped_decimals']
                name = coin_data.get("name", f"Coin {i}")
                symbol = coin_data.get("name", f"C{i}")
                contract = deployer.deploy(name, symbol, decimals, underlying, {'from': alice})
                for target, attr in fn_names.items():
                    setattr(contract, target, getattr(contract, attr))
                if coin_data.get("withdrawal_fee"):
                    contract._set_withdrawal_fee(coin_data["withdrawal_fee"], {'from': alice})
                coins.append(contract)
        yield coins


@pytest.fixture(scope="module")
def underlying_coins(MintableTestToken, ERC20Mock, ERC20MockNoReturn, alice, pool_data, is_forked):
    coins = []

    if is_forked:
        for data in pool_data['coins']:
            coins.append(MintableTestToken(data['underlying_address']))
    else:
        for i, coin_data in enumerate(pool_data['coins']):
            decimals = coin_data['decimals']
            deployer = ERC20MockNoReturn if coin_data['tethered'] else ERC20Mock
            contract = deployer.deploy(f"Underlying Coin {i}", f"UC{i}", decimals, {'from': alice})
            coins.append(contract)

    yield coins


@pytest.fixture(scope="module")
def pool_token(project, alice, pool_data):
    name = pool_data['name']
    deployer = getattr(project, pool_data['lp_contract'])
    yield deployer.deploy(f"Curve {name} LP Token", f"{name}CRV", 18, 0, {'from': alice})


@pytest.fixture(scope="module")
def swap(project, alice, underlying_coins, wrapped_coins, pool_token, pool_data, swap_mock):
    deployer = getattr(project, pool_data['swap_contract'])

    abi = next(i['inputs'] for i in deployer.abi if i['type'] == "constructor")
    args = {
        '_coins': wrapped_coins,
        '_underlying_coins': underlying_coins,
        '_pool_token': pool_token,
        '_A': 360 * 2,
        '_fee': 0,
        '_admin_fee': 0,
        '_offpeg_fee_multiplier': 0,
        '_owner': alice,
        '_y_pool': swap_mock,
    }
    deployment_args = [args[i['name']] for i in abi] + [({'from': alice})]

    contract = deployer.deploy(*deployment_args)
    pool_token.set_minter(contract, {'from': alice})

    yield contract


@pytest.fixture(scope="module")
def zap(project, alice, swap, underlying_coins, wrapped_coins, pool_token, pool_data):
    deployer = getattr(project, pool_data.get('zap_contract'), None)
    if deployer is None:
        yield False
    else:
        yield deployer.deploy(wrapped_coins, underlying_coins, swap, pool_token, {'from': alice})


@pytest.fixture(scope="module")
def registry(
    Registry,
    alice,
    gauge_controller,
    swap,
    pool_token,
    n_coins,
    wrapped_coins,
    wrapped_decimals,
    underlying_decimals,
    pool_data,
):
    registry = Registry.deploy(gauge_controller, {'from': alice})

    rate_sig = "0x00"
    if next((i for i in wrapped_coins if hasattr(i, "get_rate")), False):
        contract = next(i for i in wrapped_coins if hasattr(i, "get_rate"))
        rate_sig = right_pad(contract.get_rate.signature)
    has_initial_A = hasattr(swap, "initial_A")
    is_v1 = pool_data['lp_contract'] == "CurveTokenV1"

    if hasattr(swap, "underlying_coins"):
        registry.add_pool(
            swap,
            n_coins,
            pool_token,
            ZERO_ADDRESS,
            rate_sig,
            pack_values(wrapped_decimals),
            pack_values(underlying_decimals),
            has_initial_A,
            is_v1,
            {'from': alice}
        )
    else:
        use_rates = [i['wrapped'] for i in pool_data['coins']] + [False] * (8 - n_coins)
        registry.add_pool_without_underlying(
            swap,
            n_coins,
            pool_token,
            ZERO_ADDRESS,
            rate_sig,
            pack_values(underlying_decimals),
            pack_values(use_rates),
            has_initial_A,
            is_v1,
            {'from': alice}
        )

    yield registry


@pytest.fixture(scope="module")
def gauge_controller(GaugeControllerMock, alice):
    yield GaugeControllerMock.deploy({'from': alice})


@pytest.fixture(scope="module")
def swap_mock(SwapMock, pool_data, alice):
    if pool_data['name'] == "snow":
        yield SwapMock.deploy({'from': alice})
    else:
        yield False
