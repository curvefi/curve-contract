import pytest


@pytest.fixture(scope="module", autouse=True)
def admin_setup(accounts, pool_proxy, pool):
    # set admins as accounts[:3]
    pool_proxy.commit_set_admins(accounts[0], accounts[1], accounts[2], {'from': accounts[0]})
    pool_proxy.apply_set_admins({'from': accounts[0]})

    # set pool_proxy as owner of pool
    pool.commit_transfer_ownership(pool_proxy, {'from': accounts[0]})
    pool.apply_transfer_ownership({'from': accounts[0]})
