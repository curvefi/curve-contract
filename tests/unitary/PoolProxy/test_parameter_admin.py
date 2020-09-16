import brownie
import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

pool_parameters_mock = """

amp: public(uint256)
fee: public(uint256)
admin_fee: public(uint256)

future_amp: public(uint256)
future_fee: public(uint256)
future_admin_fee: public(uint256)

@external
def commit_new_parameters(amplification: uint256, new_fee: uint256, new_admin_fee: uint256):
    self.future_amp = amplification
    self.future_fee = new_fee
    self.future_admin_fee = new_admin_fee

@external
def apply_new_parameters():
    self.amp = self.future_amp
    self.fee = self.future_fee
    self.admin_fee = self.future_admin_fee
    self.future_amp = 0
    self.future_fee = 0
    self.future_admin_fee = 0

@external
def revert_new_parameters():
    self.future_amp = 0
    self.future_fee = 0
    self.future_admin_fee = 0
"""


@pytest.fixture(scope="module")
def param_pool(accounts):
    yield brownie.compile_source(pool_parameters_mock).Vyper.deploy({'from': accounts[0]})


def test_commit_new_fee(accounts, pool_proxy, pool):
    pool_proxy.commit_new_fee(pool, 31337, 42, {'from': accounts[1]})


@pytest.mark.parametrize('idx', range(4))
def test_apply_new_fee(accounts, pool_proxy, pool, idx):
    pool_proxy.commit_new_fee(pool, 31337, 42, {'from': accounts[1]})

    pool_proxy.apply_new_fee(pool, {'from': accounts[idx]})

    assert pool.fee() == 31337
    assert pool.admin_fee() == 42


@pytest.mark.parametrize('idx', [0, 2, 3])
def test_commit_new_fee_no_access(accounts, pool_proxy, pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.commit_new_fee(pool, 31337, 42, {'from': accounts[idx]})


def test_ramp_A(accounts, chain, pool_proxy, pool):
    time = chain.time() + 86400 * 2
    pool_proxy.ramp_A(pool, 1000, time, {'from': accounts[1]})

    assert pool.future_A() == 1000
    assert pool.future_A_time() == time


def test_stop_ramp_A(accounts, chain, pool_proxy, pool):
    initial_A = pool.initial_A()

    pool_proxy.ramp_A(pool, 1000, chain.time() + 86400 * 2, {'from': accounts[1]})
    tx = pool_proxy.stop_ramp_A(pool, {'from': accounts[1]})

    assert pool.future_A() == initial_A
    assert pool.future_A_time() == tx.timestamp


@pytest.mark.parametrize('idx', [0, 2, 3])
def test_ramp_A_no_access(accounts, chain, pool_proxy, pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.ramp_A(pool, 1000, chain.time() + 86400 * 2, {'from': accounts[idx]})


@pytest.mark.parametrize('idx', [0, 2, 3])
def test_stop_ramp_A_no_access(accounts, pool_proxy, pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.stop_ramp_A(pool, {'from': accounts[idx]})


def test_commit_new_parameters(accounts, pool_proxy, param_pool):
    pool_proxy.commit_new_parameters(param_pool, 1000, 31337, 42, {'from': accounts[1]})

    assert param_pool.future_amp() == 1000
    assert param_pool.future_fee() == 31337
    assert param_pool.future_admin_fee() == 42


@pytest.mark.parametrize('idx', [0, 2, 3])
def test_commit_new_parameters_no_access(accounts, pool_proxy, param_pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.commit_new_parameters(param_pool, 1000, 0, 0, {'from': accounts[idx]})


def test_commit_new_parameters_not_exist(accounts, pool_proxy, pool):
    with brownie.reverts('dev: if implemented by the pool'):
        pool_proxy.commit_new_parameters(pool, 1000, 0, 0, {'from': accounts[1]})


def test_apply_new_parameters(accounts, pool_proxy, param_pool):
    pool_proxy.commit_new_parameters(param_pool, 1000, 31337, 42, {'from': accounts[1]})
    pool_proxy.apply_new_parameters(param_pool, {'from': accounts[1]})

    assert param_pool.amp() == 1000
    assert param_pool.fee() == 31337
    assert param_pool.admin_fee() == 42


def test_apply_new_parameters_not_exist(accounts, pool_proxy, pool):
    with brownie.reverts('dev: if implemented by the pool'):
        pool_proxy.apply_new_parameters(pool, {'from': accounts[1]})


def test_revert_new_parameters(accounts, pool_proxy, param_pool):
    pool_proxy.commit_new_parameters(param_pool, 1000, 31337, 42, {'from': accounts[1]})
    pool_proxy.revert_new_parameters(param_pool, {'from': accounts[1]})

    assert param_pool.future_amp() == 0
    assert param_pool.future_fee() == 0
    assert param_pool.future_admin_fee() == 0


@pytest.mark.parametrize('idx', [0, 2, 3])
def test_revert_new_parameters_no_access(accounts, pool_proxy, param_pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.revert_new_parameters(param_pool, {'from': accounts[idx]})


def test_revert_new_parameters_not_exist(accounts, pool_proxy, pool):
    with brownie.reverts('dev: if implemented by the pool'):
        pool_proxy.revert_new_parameters(ZERO_ADDRESS, {'from': accounts[1]})
