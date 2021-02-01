#!/usr/bin/python3
import brownie


def test_sender_balance_decreases(alice, bob, charlie, token):
    sender_balance = token.balanceOf(alice)
    amount = sender_balance // 4

    token.approve(bob, amount, {"from": alice})
    token.transferFrom(alice, charlie, amount, {"from": bob})

    assert token.balanceOf(alice) == sender_balance - amount


def test_receiver_balance_increases(alice, bob, charlie, token):
    receiver_balance = token.balanceOf(charlie)
    amount = token.balanceOf(alice) // 4

    token.approve(bob, amount, {"from": alice})
    token.transferFrom(alice, charlie, amount, {"from": bob})

    assert token.balanceOf(charlie) == receiver_balance + amount


def test_caller_balance_not_affected(alice, bob, charlie, token):
    caller_balance = token.balanceOf(bob)
    amount = token.balanceOf(alice)

    token.approve(bob, amount, {"from": alice})
    token.transferFrom(alice, charlie, amount, {"from": bob})

    assert token.balanceOf(bob) == caller_balance


def test_caller_approval_affected(alice, bob, charlie, token):
    approval_amount = token.balanceOf(alice)
    transfer_amount = approval_amount // 4

    token.approve(bob, approval_amount, {"from": alice})
    token.transferFrom(alice, charlie, transfer_amount, {"from": bob})

    assert token.allowance(alice, bob) == approval_amount - transfer_amount


def test_receiver_approval_not_affected(alice, bob, charlie, token):
    approval_amount = token.balanceOf(alice)
    transfer_amount = approval_amount // 4

    token.approve(bob, approval_amount, {"from": alice})
    token.approve(charlie, approval_amount, {"from": alice})
    token.transferFrom(alice, charlie, transfer_amount, {"from": bob})

    assert token.allowance(alice, charlie) == approval_amount


def test_total_supply_not_affected(alice, bob, charlie, token):
    total_supply = token.totalSupply()
    amount = token.balanceOf(alice)

    token.approve(bob, amount, {"from": alice})
    token.transferFrom(alice, charlie, amount, {"from": bob})

    assert token.totalSupply() == total_supply


def test_returns_true(alice, bob, charlie, token):
    amount = token.balanceOf(alice)
    token.approve(bob, amount, {"from": alice})
    tx = token.transferFrom(alice, charlie, amount, {"from": bob})

    assert tx.return_value is True


def test_transfer_full_balance(alice, bob, charlie, token):
    amount = token.balanceOf(alice)
    receiver_balance = token.balanceOf(charlie)

    token.approve(bob, amount, {"from": alice})
    token.transferFrom(alice, charlie, amount, {"from": bob})

    assert token.balanceOf(alice) == 0
    assert token.balanceOf(charlie) == receiver_balance + amount


def test_transfer_zero_tokens(alice, bob, charlie, token):
    sender_balance = token.balanceOf(alice)
    receiver_balance = token.balanceOf(charlie)

    token.approve(bob, sender_balance, {"from": alice})
    token.transferFrom(alice, charlie, 0, {"from": bob})

    assert token.balanceOf(alice) == sender_balance
    assert token.balanceOf(charlie) == receiver_balance


def test_transfer_zero_tokens_without_approval(alice, bob, charlie, token):
    sender_balance = token.balanceOf(alice)
    receiver_balance = token.balanceOf(charlie)

    token.transferFrom(alice, charlie, 0, {"from": bob})

    assert token.balanceOf(alice) == sender_balance
    assert token.balanceOf(charlie) == receiver_balance


def test_insufficient_balance(alice, bob, charlie, token):
    balance = token.balanceOf(alice)

    token.approve(bob, balance + 1, {"from": alice})
    with brownie.reverts():
        token.transferFrom(alice, charlie, balance + 1, {"from": bob})


def test_insufficient_approval(alice, bob, charlie, token):
    balance = token.balanceOf(alice)

    token.approve(bob, balance - 1, {"from": alice})
    with brownie.reverts():
        token.transferFrom(alice, charlie, balance, {"from": bob})


def test_no_approval(alice, bob, charlie, token):
    balance = token.balanceOf(alice)

    with brownie.reverts():
        token.transferFrom(alice, charlie, balance, {"from": bob})


def test_revoked_approval(alice, bob, charlie, token):
    balance = token.balanceOf(alice)

    token.approve(bob, balance, {"from": alice})
    token.approve(bob, 0, {"from": alice})

    with brownie.reverts():
        token.transferFrom(alice, charlie, balance, {"from": bob})


def test_transfer_to_self(alice, bob, token):
    sender_balance = token.balanceOf(alice)
    amount = sender_balance // 4

    token.approve(alice, sender_balance, {"from": alice})
    token.transferFrom(alice, alice, amount, {"from": alice})

    assert token.balanceOf(alice) == sender_balance
    assert token.allowance(alice, alice) == sender_balance - amount


def test_transfer_to_self_no_approval(alice, bob, token):
    amount = token.balanceOf(alice)

    with brownie.reverts():
        token.transferFrom(alice, alice, amount, {"from": alice})


def test_transfer_event_fires(alice, bob, charlie, token):
    amount = token.balanceOf(alice)

    token.approve(bob, amount, {"from": alice})
    tx = token.transferFrom(alice, charlie, amount, {"from": bob})

    assert len(tx.events) == 1
    assert tx.events["Transfer"].values() == [alice, charlie, amount]
