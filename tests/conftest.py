import pytest

N_COINS = 2
PRECISIONS = [18, 8]

# isolation setup

@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


# named accounts

@pytest.fixture(scope="session")
def alice(accounts):
    yield accounts[0]


@pytest.fixture(scope="session")
def bob(accounts):
    yield accounts[1]


@pytest.fixture(scope="session")
def charlie(accounts):
    yield accounts[2]


# contract deployments

@pytest.fixture(scope="module")
def coins(ERC20Mock, alice):
    coins = []

    for i in range(N_COINS):
        coin = ERC20Mock.deploy(f"Coin {i}", f"C{i}", PRECISIONS[i], {'from': alice})
        coins.append(coin)

    yield coins


@pytest.fixture(scope="module")
def pool_token(CurveToken, alice):
    yield CurveToken.deploy(f"Stableswap", "STBL", 18, 0, {'from': alice})


@pytest.fixture(scope="module")
def swap(StableSwap, alice, coins, pool_token):
    contract = StableSwap.deploy(alice, coins, pool_token, 360 * 2, 0, 0, {'from': alice})
    pool_token.set_minter(contract, {'from': alice})

    yield contract


def approx(a, b, precision=1e-10):
    return 2 * abs(a - b) / (a + b) <= precision
