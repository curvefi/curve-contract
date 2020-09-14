"""
Tests specific to CurveTokenV2
"""

import pytest


@pytest.fixture(scope="module")
def tokenV2(CurveTokenV2, alice, minter):
    contract = CurveTokenV2.deploy("Test Token", "TST", 18, 100000, {'from': alice})
    contract.set_minter(minter, {'from': alice})
    yield contract


def test_burn_returns_true(tokenV2, minter, alice):
    tx = tokenV2.burnFrom(alice, 12345678, {'from': minter})

    assert tx.return_value is True


def test_mint_returns_true(tokenV2, minter, bob):
    tx = tokenV2.mint(bob, 12345678, {'from': minter})

    assert tx.return_value is True


def test_infinite_approval(tokenV2, alice, bob):
    tokenV2.approve(bob, 2**256-1, {'from': alice})
    tokenV2.transferFrom(alice, bob, 10**18, {'from': bob})

    assert tokenV2.allowance(alice, bob) == 2**256-1
