import brownie
import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


owner_functions_mock = """

aave: public(uint256)
donated: public(bool)
withdrawn: public(bool)

@external
def set_aave_referral(referral_code: uint256):
    self.aave = referral_code

@external
def donate_admin_fees():
    self.donated = True

@external
def withdraw_admin_fees():
    self.withdrawn = True
"""


@pytest.fixture(scope="module")
def owner_pool(accounts):
    yield brownie.compile_source(owner_functions_mock).Vyper.deploy({'from': accounts[0]})


def test_transfer_ownership(accounts, pool_proxy, pool):
    pool_proxy.commit_transfer_ownership(pool, accounts[4], {'from': accounts[0]})
    pool_proxy.apply_transfer_ownership(pool, {'from': accounts[0]})

    assert pool.owner() == accounts[4]


@pytest.mark.parametrize('idx', range(1, 4))
def test_commit_transfer_ownership_no_access(accounts, pool_proxy, pool, idx):
    with brownie.reverts("Access denied"):
        pool_proxy.commit_transfer_ownership(pool, accounts[4], {'from': accounts[idx]})


@pytest.mark.parametrize('idx', range(0, 4))
def test_apply_transfer_ownership_no_access(accounts, pool_proxy, pool, idx):
    pool_proxy.commit_transfer_ownership(pool, accounts[4], {'from': accounts[0]})
    pool_proxy.apply_transfer_ownership(pool, {'from': accounts[idx]})


def test_cancel_transfer_ownership(accounts, pool_proxy, pool):
    pool_proxy.commit_transfer_ownership(pool, accounts[4], {'from': accounts[0]})
    pool_proxy.revert_transfer_ownership(pool, {'from': accounts[0]})

    with brownie.reverts():
        pool_proxy.apply_transfer_ownership(pool, {'from': accounts[0]})


@pytest.mark.parametrize('idx', range(1, 4))
def test_cancel_transfer_ownership_no_access(accounts, pool_proxy, pool, idx):
    pool_proxy.commit_transfer_ownership(pool, accounts[4], {'from': accounts[0]})
    with brownie.reverts("Access denied"):
        pool_proxy.revert_transfer_ownership(pool, {'from': accounts[idx]})


def test_set_aave_referral(accounts, pool_proxy, owner_pool):
    pool_proxy.set_aave_referral(owner_pool, 42, {'from': accounts[0]})

    assert owner_pool.aave() == 42


def test_set_aave_referral_not_exists(accounts, pool_proxy, pool):
    with brownie.reverts():
        pool_proxy.set_aave_referral(pool, 42, {'from': accounts[0]})


@pytest.mark.parametrize('idx', range(1, 4))
def test_set_aave_referral_no_access(accounts, pool_proxy, owner_pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.set_aave_referral(owner_pool, 42, {'from': accounts[idx]})


def test_donate_fees(accounts, pool_proxy, owner_pool):
    pool_proxy.donate_admin_fees(owner_pool, {'from': accounts[0]})

    assert owner_pool.donated() is True


def test_donate_fees_not_exists(accounts, pool_proxy, pool):
    with brownie.reverts():
        pool_proxy.donate_admin_fees(pool, {'from': accounts[0]})


@pytest.mark.parametrize('idx', range(1, 4))
def test_donate_fees_no_access(accounts, pool_proxy, owner_pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.donate_admin_fees(owner_pool, {'from': accounts[idx]})


@pytest.mark.parametrize('idx', range(4))
def test_withdraw_admin_fees(accounts, pool_proxy, owner_pool, idx):
    pool_proxy.withdraw_admin_fees(owner_pool, {'from': accounts[idx]})

    assert owner_pool.withdrawn() is True


@pytest.mark.parametrize('idx', range(1, 4))
def test_set_burner_no_access(accounts, pool_proxy, token, idx):
    with brownie.reverts("Access denied"):
        pool_proxy.set_burner(token, accounts[1], {'from': accounts[idx]})


def test_set_burner(accounts, pool_proxy, token):
    pool_proxy.set_burner(token, accounts[4], {'from': accounts[0]})

    assert token.allowance(pool_proxy, accounts[4]) == 2**256-1


def test_unset_burner(accounts, pool_proxy, token):
    pool_proxy.set_burner(token, accounts[4], {'from': accounts[0]})
    pool_proxy.set_burner(token, ZERO_ADDRESS, {'from': accounts[0]})

    assert token.allowance(pool_proxy, accounts[4]) == 0


def test_modify_burner(accounts, pool_proxy, token):
    pool_proxy.set_burner(token, accounts[4], {'from': accounts[0]})
    pool_proxy.set_burner(token, accounts[5], {'from': accounts[0]})

    assert token.allowance(pool_proxy, accounts[4]) == 0
    assert token.allowance(pool_proxy, accounts[5]) == 2**256-1
