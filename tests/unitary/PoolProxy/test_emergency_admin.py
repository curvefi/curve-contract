import brownie
import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_kill(accounts, pool_proxy, pool):
    pool_proxy.kill_me(pool, {'from': accounts[2]})


@pytest.mark.parametrize('idx', [0, 2])
def test_unkill(accounts, pool_proxy, pool, idx):
    pool_proxy.unkill_me(pool, {'from': accounts[idx]})


@pytest.mark.parametrize('idx', [0, 1, 3])
def test_kill_no_access(accounts, pool_proxy, pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.kill_me(pool, {'from': accounts[idx]})


@pytest.mark.parametrize('idx', [1, 3])
def test_unkill_no_access(accounts, pool_proxy, pool, idx):
    with brownie.reverts('Access denied'):
        pool_proxy.unkill_me(pool, {'from': accounts[idx]})
