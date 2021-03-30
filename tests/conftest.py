import json
import warnings
from pathlib import Path

import pytest
from brownie._config import CONFIG
from brownie.project.main import get_loaded_projects

# functions in wrapped methods are renamed to simplify common tests

WRAPPED_COIN_METHODS = {
    "ATokenMock": {"get_rate": "_get_rate", "mint": "mint"},
    "cERC20": {"get_rate": "exchangeRateStored", "mint": "mint"},
    "IdleToken": {"get_rate": "tokenPrice", "mint": "mintIdleToken"},
    "renERC20": {"get_rate": "exchangeRateCurrent"},
    "yERC20": {"get_rate": "getPricePerFullShare", "mint": "deposit"},
    "aETH": {"get_rate": "ratio"},
    "rETH": {"get_rate": "getExchangeRate"},
}

pytest_plugins = [
    "fixtures.accounts",
    "fixtures.coins",
    "fixtures.deployments",
    "fixtures.functions",
    "fixtures.pooldata",
    "fixtures.setup",
]

_pooldata = {}


def pytest_addoption(parser):
    parser.addoption("--pool", help="comma-separated list of pools to target")
    parser.addoption("--unitary", action="store_true", help="only run unit tests")
    parser.addoption("--integration", action="store_true", help="only run integration tests")


def pytest_configure(config):
    # add custom markers
    config.addinivalue_line("markers", "target_pool: run test against one or more specific pool")
    config.addinivalue_line("markers", "skip_pool: exclude one or more pools in this test")
    config.addinivalue_line(
        "markers", "skip_pool_type: exclude one or more pool types in this test"
    )
    config.addinivalue_line("markers", "lending: only run test against pools that involve lending")
    config.addinivalue_line("markers", "zap: only run test against pools with a deposit contract")
    config.addinivalue_line(
        "markers",
        "itercoins: parametrize a test with one or more ranges, equal to the length "
        "of `wrapped_coins` for the active pool",
    )


def pytest_sessionstart():
    # load `pooldata.json` for each pool
    project = get_loaded_projects()[0]
    for path in [i for i in project._path.glob("contracts/pools/*") if i.is_dir()]:
        with path.joinpath("pooldata.json").open() as fp:
            _pooldata[path.name] = json.load(fp)
            _pooldata[path.name].update(
                name=path.name, swap_contract=next(i.stem for i in path.glob("StableSwap*"))
            )
            zap_contract = next((i.stem for i in path.glob("Deposit*")), None)
            if zap_contract:
                _pooldata[path.name]["zap_contract"] = zap_contract

    # create pooldata for templates
    lp_contract = sorted(i._name for i in project if i._name.startswith("CurveToken"))[-1]

    for path in [i for i in project._path.glob("contracts/pool-templates/*") if i.is_dir()]:
        with path.joinpath("pooldata.json").open() as fp:
            name = f"template-{path.name}"
            _pooldata[name] = json.load(fp)
            _pooldata[name].update(
                name=name,
                lp_contract=lp_contract,
                swap_contract=next(i.stem for i in path.glob("*Swap*")),
            )
            zap_contract = next((i.stem for i in path.glob("Deposit*")), None)
            if zap_contract:
                _pooldata[name]["zap_contract"] = zap_contract

    for _, data in _pooldata.items():
        if "base_pool" in data:
            data["base_pool"] = _pooldata[data["base_pool"]]
        elif "base_pool_contract" in data:
            # for metapool templates, we target a contract instead of a specific pool
            base_swap = data["base_pool_contract"]
            base_data = next(v for v in _pooldata.values() if v["swap_contract"] == base_swap)
            data["base_pool"] = base_data


def pytest_ignore_collect(path, config):
    project = get_loaded_projects()[0]
    path = Path(path).relative_to(project._path)
    path_parts = path.parts[1:-1]

    if path.is_dir():
        return None

    # always collect fixtures
    if path_parts[:1] == ("fixtures",):
        return None

    # always allow forked tests
    if path_parts[:1] == ("forked",):
        return None

    # with the `--unitary` flag, skip any tests in an `integration` subdirectory
    if config.getoption("unitary") and "integration" in path_parts:
        return True

    # with the `--integration` flag, skip any tests NOT in an `integration` subdirectory
    if config.getoption("integration") and "integration" not in path_parts:
        return True

    if config.getoption("pool") and path_parts:
        # with a specific pool targeted, only run pool and zap tests
        if path_parts[0] not in ("pools", "zaps"):
            return True

        # always run common tests
        if path_parts[1] == "common":
            return None

        target_pools = config.getoption("pool").split(",")

        # only include metapool tests if at least one targeted pool is a metapool
        if path_parts[1] == "meta":
            return next(
                (None for i in target_pools if "meta" in _pooldata[i].get("pool_types", [])), True
            )

        # only include a-style tests if at least one targeted pool is an a-style pool
        if path_parts[1] == "arate":
            return next(
                (None for i in target_pools if "arate" in _pooldata[i].get("pool_types", [])), True
            )

        # only include c-style tests if at least one targeted pool is an c-style pool
        if path_parts[1] == "crate":
            return next(
                (None for i in target_pools if "crate" in _pooldata[i].get("pool_type", [])), True
            )

        # only include eth tests if at least one targeted pool is an eth pool
        if path_parts[1] == "eth":
            return next(
                (None for i in target_pools if "eth" in _pooldata[i].get("pool_type", [])), True
            )

        # filter other pool-specific folders
        if path_parts[1] not in target_pools:
            return True


def pytest_generate_tests(metafunc):
    project = get_loaded_projects()[0]
    itercoins_bound = max(len(i["coins"]) for i in _pooldata.values())
    if "pool_data" in metafunc.fixturenames:
        # parametrize `pool_data`
        test_path = Path(metafunc.definition.fspath).relative_to(project._path)
        if test_path.parts[1] in ("pools", "zaps"):
            if test_path.parts[2] in ("common", "meta", "crate", "arate", "eth"):
                # parametrize common pool/zap tests to run against all pools
                if metafunc.config.getoption("pool"):
                    params = metafunc.config.getoption("pool").split(",")
                else:
                    params = list(_pooldata)
                # parameterize based on pool type
                if test_path.parts[2] == "meta":
                    params = [i for i in params if "meta" in _pooldata[i].get("pool_types", [])]
                if test_path.parts[2] == "arate":
                    params = [i for i in params if "arate" in _pooldata[i].get("pool_types", [])]
                if test_path.parts[2] == "crate":
                    params = [i for i in params if "crate" in _pooldata[i].get("pool_types", [])]
                if test_path.parts[2] == "eth":
                    params = [i for i in params if "eth" in _pooldata[i].get("pool_types", [])]

            else:
                # run targetted pool/zap tests against only the specific pool
                params = [test_path.parts[2]]

            if test_path.parts[1] == "zaps":
                # for zap tests, filter by pools that have a Deposit contract
                params = [i for i in params if _pooldata[i].get("zap_contract")]
        else:
            # pool tests outside `tests/pools` or `tests/zaps` will only run when
            # a target pool is explicitly declared
            try:
                params = metafunc.config.getoption("pool").split(",")
            except Exception:
                params = []
                warnings.warn(
                    f"'{test_path.as_posix()}' contains pool tests, but is outside of "
                    "'tests/pools/'. To run it, specify a pool with `--pool [name]`"
                )
        metafunc.parametrize("pool_data", params, indirect=True, scope="session")

        # apply initial parametrization of `itercoins`
        for marker in metafunc.definition.iter_markers(name="itercoins"):
            for item in marker.args:
                metafunc.parametrize(item, range(itercoins_bound))


def pytest_collection_modifyitems(config, items):
    project = get_loaded_projects()[0]
    try:
        is_forked = "fork" in CONFIG.active_network["id"]
    except Exception:
        is_forked = False

    for item in items.copy():
        try:
            params = item.callspec.params
            data = _pooldata[params["pool_data"]]
        except Exception:
            continue

        # during forked tests, filter pools where pooldata does not contain deployment addresses
        if is_forked and next((i for i in data["coins"] if "underlying_address" not in i), False):
            items.remove(item)
            continue

        # remove excess `itercoins` parametrized tests
        for marker in item.iter_markers(name="itercoins"):
            n_coins = len(data["coins"])

            # for metapools, consider the base pool when calculating n_coins
            if marker.kwargs.get("underlying") and "base_pool" in data:
                n_coins = len(data["base_pool"]["coins"]) + 1

            values = [params[i] for i in marker.args]
            if max(values) >= n_coins or len(set(values)) < len(values):
                items.remove(item)
                break

        if item not in items:
            continue

        # apply `skip_pool` marker
        for marker in item.iter_markers(name="skip_pool"):
            if params["pool_data"] in marker.args:
                items.remove(item)
                break

        if item not in items:
            continue

        # apply `skip_pool_type` marker
        for marker in item.iter_markers(name="skip_pool_type"):
            if len(set(data.get("pool_types", [])) & set(marker.args)):
                items.remove(item)
                break

        if item not in items:
            continue

        # apply `target_pool` marker
        for marker in item.iter_markers(name="target_pool"):
            if params["pool_data"] not in marker.args:
                items.remove(item)
                break

        if item not in items:
            continue

        # apply `lending` marker
        if next(item.iter_markers(name="lending"), False):
            deployer = getattr(project, data["swap_contract"])
            if "exchange_underlying" not in deployer.signatures:
                items.remove(item)
                continue

        # apply `zap` marker
        if next(item.iter_markers(name="zap"), False) and "zap_contract" not in data:
            items.remove(item)
            continue

    # hacky magic to ensure the correct number of tests is shown in collection report
    config.pluginmanager.get_plugin("terminalreporter")._numcollected = len(items)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        # because of how tests are filtered in the CI, we treat "no tests collected" as passing
        session.exitstatus = pytest.ExitCode.OK


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
        # ("tests", "pools" or "zaps", pool_name, ...)
        pool_name = test_path.parts[2]
    return _pooldata[pool_name]


@pytest.fixture(scope="module")
def base_pool_data(pool_data):
    return pool_data.get("base_pool", None)


@pytest.fixture(scope="session")
def project():
    yield get_loaded_projects()[0]


@pytest.fixture(scope="session")
def is_forked():
    yield "fork" in CONFIG.active_network["id"]
