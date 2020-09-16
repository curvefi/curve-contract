import brownie
import pytest


@pytest.fixture(scope="module", autouse=True)
def deposit_setup(accounts, liquidity_gauge, mock_lp_token):
    mock_lp_token.approve(liquidity_gauge, 2 ** 256 - 1, {"from": accounts[0]})


def test_deposit(accounts, liquidity_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])
    liquidity_gauge.deposit(100000, {'from': accounts[0]})

    assert mock_lp_token.balanceOf(liquidity_gauge) == 100000
    assert mock_lp_token.balanceOf(accounts[0]) == balance - 100000
    assert liquidity_gauge.totalSupply() == 100000
    assert liquidity_gauge.balanceOf(accounts[0]) == 100000


def test_deposit_zero(accounts, liquidity_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])
    liquidity_gauge.deposit(0, {'from': accounts[0]})

    assert mock_lp_token.balanceOf(liquidity_gauge) == 0
    assert mock_lp_token.balanceOf(accounts[0]) == balance
    assert liquidity_gauge.totalSupply() == 0
    assert liquidity_gauge.balanceOf(accounts[0]) == 0


def test_deposit_insufficient_balance(accounts, liquidity_gauge, mock_lp_token):
    with brownie.reverts():
        liquidity_gauge.deposit(100000, {'from': accounts[1]})


def test_withdraw(accounts, liquidity_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])

    liquidity_gauge.deposit(100000, {'from': accounts[0]})
    liquidity_gauge.withdraw(100000, {'from': accounts[0]})

    assert mock_lp_token.balanceOf(liquidity_gauge) == 0
    assert mock_lp_token.balanceOf(accounts[0]) == balance
    assert liquidity_gauge.totalSupply() == 0
    assert liquidity_gauge.balanceOf(accounts[0]) == 0


def test_withdraw_zero(accounts, liquidity_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])
    liquidity_gauge.deposit(100000, {'from': accounts[0]})
    liquidity_gauge.withdraw(0, {'from': accounts[0]})

    assert mock_lp_token.balanceOf(liquidity_gauge) == 100000
    assert mock_lp_token.balanceOf(accounts[0]) == balance - 100000
    assert liquidity_gauge.totalSupply() == 100000
    assert liquidity_gauge.balanceOf(accounts[0]) == 100000


def test_withdraw_new_epoch(accounts, chain, liquidity_gauge, mock_lp_token):
    balance = mock_lp_token.balanceOf(accounts[0])

    liquidity_gauge.deposit(100000, {'from': accounts[0]})
    chain.sleep(86400 * 400)
    liquidity_gauge.withdraw(100000, {'from': accounts[0]})

    assert mock_lp_token.balanceOf(liquidity_gauge) == 0
    assert mock_lp_token.balanceOf(accounts[0]) == balance
    assert liquidity_gauge.totalSupply() == 0
    assert liquidity_gauge.balanceOf(accounts[0]) == 0
