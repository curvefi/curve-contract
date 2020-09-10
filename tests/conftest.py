from brownie.project.main import get_loaded_projects
import pytest
from pathlib import Path
import json

# functions in wrapped methods are renamed to simplify common tests
WRAPPED_COIN_METHODS = {
    "cERC20": {
        "get_rate": "exchangeRateStored",
        "mint": "mint",
    },
    "renERC20": {
        "get_rate": "exchangeRateCurrent",
        "mint": "mint",
    },
    "yERC20": {
        "get_rate": "getPricePerFullShare",
        "mint": "deposit",
    },
}


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
_pooldata = {}


def pytest_addoption(parser):
    parser.addoption("--pool", help="comma-separated list of pools to target",)


def pytest_configure(config):
    # add custom markers
    config.addinivalue_line("markers", "target_pool: run test against one or more specific pool")
    config.addinivalue_line("markers", "skip_pool: exclude one or more pools in this test")
    config.addinivalue_line(
        "markers",
        "itercoins: parametrize a test with one or more ranges, equal to the length "
        "of `wrapped_coins` for the active pool"
    )


def pytest_sessionstart():
    # load `pooldata.json` for each pool
    project = get_loaded_projects()[0]
    for path in [i for i in project._path.glob("contracts/pools/*") if i.is_dir()]:
        with path.joinpath('pooldata.json').open() as fp:
            _pooldata[path.name] = json.load(fp)
            _pooldata[path.name]['name'] = path.name


def pytest_generate_tests(metafunc):
    project = get_loaded_projects()[0]
    itercoins_bound = max(len(i['coins']) for i in _pooldata.values())

    if "pool_data" in metafunc.fixturenames:
        # parametrize `pool_data`
        test_path = Path(metafunc.definition.fspath).relative_to(project._path)
        if test_path.parts[1] == "common":
            if metafunc.config.getoption("pool"):
                params = metafunc.config.getoption("pool").split(',')
            else:
                params = list(_pooldata)
            metafunc.parametrize("pool_data", params, indirect=True, scope="session")

        # apply initial parametrization of `itercoins`
        for marker in metafunc.definition.iter_markers(name="itercoins"):
            for item in marker.args:
                metafunc.parametrize(item, range(itercoins_bound))


def pytest_collection_modifyitems(config, items):
    for item in items.copy():
        params = item.callspec.params
        data = _pooldata[params['pool_data']]

        # remove excess `itercoins` parametrized tests
        if next(item.iter_markers(name="itercoins"), None):
            values = [i for i in params.values() if isinstance(i, int)]
            if max(values) >= len(data['coins']) or len(set(values)) < len(values):
                items.remove(item)
                continue

        # apply `skip_pool` marker
        for marker in item.iter_markers(name="skip_pool"):
            if params["pool_data"] in marker.args:
                items.remove(item)
                continue

        # apply `target_pool` marker
        for marker in item.iter_markers(name="target_pool"):
            if params["pool_data"] not in marker.args:
                items.remove(item)
                continue

    # hacky magic to ensure the correct number of tests is shown in collection report
    config.pluginmanager.get_plugin("terminalreporter")._numcollected = len(items)


# isolation setup

@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


# main parametrized fixture, used to pass data about each pool into the other fixtures

@pytest.fixture(scope="session")
def pool_data(request):
    project = get_loaded_projects()[0]

    if hasattr(request, "param"):
        pool_name = request.param
    else:
        test_path = Path(request.fspath).relative_to(project._path)
        pool_name = test_path.parts[1]
    yield _pooldata[pool_name]


# pool-dependent data fixtures

@pytest.fixture(scope="module")
def underlying_decimals(pool_data):
    # number of decimal places for each underlying coin in the active pool
    yield [i['decimals'] for i in pool_data['coins']]


@pytest.fixture(scope="module")
def wrapped_decimals(pool_data):
    # number of decimal places for each wrapped coin in the active pool
    yield [i.get('wrapped_decimals', i['decimals']) for i in pool_data['coins']]


@pytest.fixture(scope="module")
def initial_amounts(wrapped_decimals):
    # 1e6 of each coin - used to make an even initial deposit in many test setups
    yield [10**(i+6) for i in wrapped_decimals]


@pytest.fixture(scope="module")
def n_coins(pool_data):
    yield len(pool_data['coins'])


# named accounts

@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[2]


@pytest.fixture(scope="session")
def project():
    yield get_loaded_projects()[0]


# contract deployments

@pytest.fixture(scope="module")
def wrapped_coins(project, alice, pool_data, underlying_coins):
    if not pool_data.get("wrapped_contract"):
        yield underlying_coins
    else:
        fn_names = WRAPPED_COIN_METHODS[pool_data['wrapped_contract']]
        deployer = getattr(project, pool_data['wrapped_contract'])
        coins = []
        for i, coin_data in enumerate(pool_data['coins']):
            underlying = underlying_coins[i]
            if not coin_data['wrapped']:
                coins.append(underlying)
            else:
                decimals = coin_data['wrapped_decimals']
                contract = deployer.deploy(
                    f"Coin {i}", f"C{i}", decimals, 0, underlying, 10**18, {'from': alice}
                )
                for target, attr in fn_names.items():
                    setattr(contract, target, getattr(contract, attr))
                coins.append(contract)

        yield coins


@pytest.fixture(scope="module")
def underlying_coins(ERC20Mock, ERC20MockNoReturn, alice, pool_data):
    coins = []
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
@pytest.mark.parametrize()
def swap(project, alice, underlying_coins, wrapped_coins, pool_token, pool_data):
    name = pool_data['name']
    swap_name = next(i.stem for i in project._path.glob(f"contracts/pools/{name}/StableSwap*"))
    deployer = getattr(project, swap_name)

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
    }
    deployment_args = [args[i['name']] for i in abi] + [({'from': alice})]

    contract = deployer.deploy(*deployment_args)
    pool_token.set_minter(contract, {'from': alice})

    yield contract


# helper functions

@pytest.fixture(scope="session")
def approx():

    def _approx(a, b, precision=1e-10):
        return 2 * abs(a - b) / (a + b) <= precision

    yield _approx
