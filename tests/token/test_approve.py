#!/usr/bin/python3

import brownie
import pytest


@pytest.mark.parametrize("idx", range(5))
def test_initial_approval_is_zero(token, alice, accounts, idx):
    assert token.allowance(alice, accounts[idx]) == 0


def test_approve(token, alice, bob):
    token.approve(bob, 10 ** 19, {"from": alice})

    assert token.allowance(alice, bob) == 10 ** 19


@pytest.mark.target_token(max=2)
def test_modify_approve_nonzero(token, alice, bob):
    token.approve(bob, 10 ** 19, {"from": alice})

    with brownie.reverts():
        token.approve(bob, 12345678, {"from": alice})


def test_modify_approve_zero_nonzero(token, alice, bob):
    token.approve(bob, 10 ** 19, {"from": alice})
    token.approve(bob, 0, {"from": alice})
    token.approve(bob, 12345678, {"from": alice})

    assert token.allowance(alice, bob) == 12345678


def test_revoke_approve(token, alice, bob):
    token.approve(bob, 10 ** 19, {"from": alice})
    token.approve(bob, 0, {"from": alice})

    assert token.allowance(alice, bob) == 0


def test_approve_self(token, alice, bob):
    token.approve(alice, 10 ** 19, {"from": alice})

    assert token.allowance(alice, alice) == 10 ** 19


def test_only_affects_target(token, alice, bob):
    token.approve(bob, 10 ** 19, {"from": alice})

    assert token.allowance(bob, alice) == 0


def test_returns_true(token, alice, bob):
    tx = token.approve(bob, 10 ** 19, {"from": alice})

    assert tx.return_value is True


def test_approval_event_fires(alice, bob, token):
    tx = token.approve(bob, 10 ** 19, {"from": alice})

    assert len(tx.events) == 1
    assert tx.events["Approval"].values() == [alice, bob, 10 ** 19]


@pytest.mark.target_token(min=2)
def test_infinite_approval(token, alice, bob):
    token.approve(bob, 2 ** 256 - 1, {"from": alice})
    token.transferFrom(alice, bob, 10 ** 18, {"from": bob})

    assert token.allowance(alice, bob) == 2 ** 256 - 1


@pytest.mark.target_token(min=3)
def test_increase_allowance(token, alice, bob):
    token.approve(bob, 100, {"from": alice})
    token.increaseAllowance(bob, 403, {"from": alice})

    assert token.allowance(alice, bob) == 503


@pytest.mark.target_token(min=3)
def test_decrease_allowance(token, alice, bob):
    token.approve(bob, 100, {"from": alice})
    token.decreaseAllowance(bob, 34, {"from": alice})

    assert token.allowance(alice, bob) == 66
