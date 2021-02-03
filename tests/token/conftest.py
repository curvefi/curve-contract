#!/usr/bin/python3

import pytest
from brownie.project.main import get_loaded_projects


def pytest_configure(config):
    # add custom markers
    config.addinivalue_line(
        "markers", "target_token: only run test against certain token contracts"
    )


def pytest_generate_tests(metafunc):
    project = get_loaded_projects()[0]
    if "token" in metafunc.fixturenames:
        params = [i for i in project if i._name.startswith("CurveToken")]
        metafunc.parametrize("token", params, indirect=True, scope="module")


def pytest_collection_modifyitems(config, items):
    for item in items.copy():
        try:
            params = item.callspec.params
        except Exception:
            continue

        # remove invalid `target_token` parametrized tests
        for marker in item.iter_markers(name="target_token"):
            lower = marker.kwargs.get("min", float("-inf"))
            upper = marker.kwargs.get("max", float("inf"))
            version = int(params["token"]._name[-1])
            if version < lower or version > upper:
                items.remove(item)


@pytest.fixture(scope="module")
def token(request, alice, minter):
    # parametrized fixture that uses every token contract in `contracts/tokens`
    deployer = request.param
    args = ["Test Token", "TST", 18, 0][: len(deployer.deploy.abi["inputs"])]
    contract = deployer.deploy(*args, {"from": alice})
    contract.set_minter(minter, {"from": alice})
    contract.mint(alice, 100000 * 10 ** 18, {"from": minter})

    yield contract


@pytest.fixture(scope="module")
def minter(accounts):
    yield accounts[-1]
