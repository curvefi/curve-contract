import brownie
import pytest

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

burner_mock = """

is_burned: public(bool)
burned_coin: public(address)

@external
def burn() -> bool:
    self.is_burned = True
    return True

@external
@payable
def burn_eth() -> bool:
    return True

@external
def burn_coin(_coin: address) -> bool:
    self.burned_coin = _coin
    return True
"""


@pytest.fixture(scope="module")
def burner(accounts, pool_proxy, coin_a):
    contract = brownie.compile_source(burner_mock).Vyper.deploy({'from': accounts[0]})
    pool_proxy.set_burner(coin_a, contract, {'from': accounts[0]})
    pool_proxy.set_burner(ZERO_ADDRESS, contract, {'from': accounts[0]})

    yield contract


@pytest.mark.parametrize('idx', range(4))
def test_burn(accounts, pool_proxy, burner, idx):
    pool_proxy.burn(burner, {'from': accounts[idx]})

    assert burner.is_burned() is True


@pytest.mark.parametrize('idx', range(4))
def test_burn_coin(accounts, pool_proxy, coin_a, burner, idx):
    pool_proxy.burn_coin(coin_a, {'from': accounts[idx]})

    assert burner.burned_coin() == coin_a


@pytest.mark.parametrize('idx', range(4))
def test_burn_eth(accounts, pool_proxy, burner, idx):
    pool_proxy.burn_eth({'from': accounts[idx], 'value': 31337})

    assert pool_proxy.balance() == 0
    assert burner.balance() == 31337


def test_burn_not_exists(accounts, pool_proxy, pool):
    with brownie.reverts():  # TODO 'dev: should implement burn()' when Brownie is fixed
        pool_proxy.burn(pool, {'from': accounts[0]})


def test_burn_coin_not_exists(accounts, pool_proxy, coin_b):
    with brownie.reverts('dev: should implement burn_coin()'):
        pool_proxy.burn_coin(coin_b, {'from': accounts[0]})


def test_burn_eth_not_exists(accounts, pool_proxy, burner):
    pool_proxy.set_burner(ZERO_ADDRESS, ZERO_ADDRESS, {'from': accounts[0]})
    with brownie.reverts('dev: should implement burn_eth()'):
        pool_proxy.burn_eth({'from': accounts[0], 'value': 1})
