import brownie
import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_assumptions(token, alice, bob, minter):
    assert token.totalSupply() == token.balanceOf(alice)
    assert token.balanceOf(bob) == 0
    assert token.balanceOf(minter) == 0


def test_set_minter(token, minter, alice):
    token.set_minter(alice, {"from": minter})


def test_only_minter(token, minter, alice):
    with brownie.reverts():
        token.set_minter(alice, {"from": alice})


@pytest.mark.target_token(max=2)
def test_transferFrom_without_approval(token, minter, alice, bob):
    balance = token.balanceOf(alice)

    # minter should be able to call transferFrom without prior approval
    token.transferFrom(alice, bob, 10 ** 19, {"from": minter})

    assert token.balanceOf(alice) == balance - 10 ** 19
    assert token.balanceOf(bob) == 10 ** 19


def test_mint_affects_balance(token, minter, bob):
    token.mint(bob, 12345678, {"from": minter})

    assert token.balanceOf(bob) == 12345678


def test_mint_affects_totalSupply(token, minter, bob):
    total_supply = token.totalSupply()

    token.mint(bob, 12345678, {"from": minter})

    assert token.totalSupply() == total_supply + 12345678


def test_mint_overflow(token, minter, bob):
    amount = 2 ** 256 - token.totalSupply()

    with brownie.reverts():
        token.mint(bob, amount, {"from": minter})


def test_mint_not_minter(token, alice):
    with brownie.reverts():
        token.mint(alice, 12345678, {"from": alice})


@pytest.mark.target_token(max=2)
def test_mint_zero_address(token, minter):
    with brownie.reverts():
        token.mint(ZERO_ADDRESS, 10 ** 18, {"from": minter})


def test_burn_affects_balance(token, minter, alice):
    balance = token.balanceOf(alice)
    token.burnFrom(alice, 12345678, {"from": minter})

    assert token.balanceOf(alice) == balance - 12345678


def test_burn_affects_totalSupply(token, minter, alice):
    total_supply = token.totalSupply()

    token.burnFrom(alice, 12345678, {"from": minter})

    assert token.totalSupply() == total_supply - 12345678


def test_burn_underflow(token, minter, alice):
    amount = token.balanceOf(alice) + 1

    with brownie.reverts():
        token.burnFrom(alice, amount, {"from": minter})


def test_burn_not_minter(token, alice):
    with brownie.reverts():
        token.burnFrom(alice, 12345678, {"from": alice})


@pytest.mark.target_token(max=2)
def test_burn_zero_address(token, alice, minter):
    token.transfer(ZERO_ADDRESS, 10 ** 18, {"from": alice})

    with brownie.reverts():
        token.burnFrom(ZERO_ADDRESS, 10 ** 18, {"from": minter})


@pytest.mark.target_token(min=2)
def test_burn_returns_true(token, minter, alice):
    tx = token.burnFrom(alice, 12345678, {"from": minter})

    assert tx.return_value is True


@pytest.mark.target_token(min=2)
def test_mint_returns_true(token, minter, bob):
    tx = token.mint(bob, 12345678, {"from": minter})

    assert tx.return_value is True
