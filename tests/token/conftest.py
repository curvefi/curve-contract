#!/usr/bin/python3

import pytest
from brownie.project.main import get_loaded_projects


def pytest_generate_tests(metafunc):
    project = get_loaded_projects()[0]
    if "token" in metafunc.fixturenames:
        params = [i for i in project if i._name.startswith("CurveToken")]
        metafunc.parametrize("token", params, indirect=True, scope="module")


@pytest.fixture(scope="module")
def token(request, alice, minter):
    # parametrized fixture that uses every token contract in `contracts/tokens`
    deployer = request.param
    contract = deployer.deploy("Test Token", "TST", 18, 100000, {'from': alice})
    contract.set_minter(minter, {'from': alice})
    yield contract


@pytest.fixture(scope="module")
def minter(accounts):
    yield accounts[-1]
