import json
import pytest

from brownie.project.main import get_loaded_projects
from pathlib import Path

from brownie_hooks import DECIMALS as hook_decimals

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

pytest_plugins = [
    "fixtures.accounts",
    "fixtures.deployments",
    "fixtures.functions",
    "fixtures.pooldata",
    "fixtures.setup",
]

_pooldata = {}


def pytest_addoption(parser):
    parser.addoption("--pool", help="comma-separated list of pools to target",)


def pytest_configure(config):
    # add custom markers
    config.addinivalue_line("markers", "target_pool: run test against one or more specific pool")
    config.addinivalue_line("markers", "skip_pool: exclude one or more pools in this test")
    config.addinivalue_line("markers", "lending: only run test against pools that involve lending")
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
            _pooldata[path.name].update(
                name=path.name,
                swap_contract=next(i.stem for i in path.glob(f"StableSwap*"))
            )

    # create pooldata for templates
    lp_contract = sorted(i._name for i in project if i._name.startswith("CurveToken"))[-1]
    _pooldata['template-y'] = {
        "name": "template-y",
        "swap_contract": "StableSwapYLend",
        "lp_contract": lp_contract,
        "wrapped_contract": "yERC20",
        "coins": [
            {"decimals": i, "tethered": bool(i), "wrapped": True, "wrapped_decimals": i}
            for i in hook_decimals
        ]
    }
    _pooldata['template-base'] = {
        "name": "template-base",
        "swap_contract": "StableSwapBase",
        "lp_contract": lp_contract,
        "coins": [{"decimals": i, "tethered": bool(i), "wrapped": False} for i in hook_decimals]
    }


def pytest_generate_tests(metafunc):
    project = get_loaded_projects()[0]
    itercoins_bound = max(len(i['coins']) for i in _pooldata.values())

    if "pool_data" in metafunc.fixturenames:
        # parametrize `pool_data`
        test_path = Path(metafunc.definition.fspath).relative_to(project._path)
        if test_path.parts[:2] == ("tests", "pools"):
            if test_path.parts[2] == "common":
                # run `tests/pools/common` tests against all pools
                if metafunc.config.getoption("pool"):
                    params = metafunc.config.getoption("pool").split(',')
                else:
                    params = list(_pooldata)
            else:
                # run `tests/pools/<POOL>` tests against only the specific pool
                params = [test_path.parts[2]]
            metafunc.parametrize("pool_data", params, indirect=True, scope="session")

        # apply initial parametrization of `itercoins`
        for marker in metafunc.definition.iter_markers(name="itercoins"):
            for item in marker.args:
                metafunc.parametrize(item, range(itercoins_bound))


def pytest_collection_modifyitems(config, items):
    project = get_loaded_projects()[0]
    for item in items.copy():
        try:
            params = item.callspec.params
            data = _pooldata[params['pool_data']]
        except Exception:
            continue

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

        # apply `target_pool` marker
        for marker in item.iter_markers(name="target_pool"):
            if params["pool_data"] not in marker.args:
                items.remove(item)

        # apply `lending` marker
        for marker in item.iter_markers(name="lending"):
            deployer = getattr(project, data['swap_contract'])
            if "exchange_underlying" not in deployer.signatures:
                items.remove(item)

    # hacky magic to ensure the correct number of tests is shown in collection report
    config.pluginmanager.get_plugin("terminalreporter")._numcollected = len(items)


# isolation setup

@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


# main parametrized fixture, used to pass data about each pool into the other fixtures

@pytest.fixture(scope="module")
def pool_data(request):
    project = get_loaded_projects()[0]

    if hasattr(request, "param"):
        pool_name = request.param
    else:
        test_path = Path(request.fspath).relative_to(project._path)
        # ("tests", "pools", pool_name, ...)
        pool_name = test_path.parts[2]
    yield _pooldata[pool_name]


@pytest.fixture(scope="session")
def project():
    yield get_loaded_projects()[0]
