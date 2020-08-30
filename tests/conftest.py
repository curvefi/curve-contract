import pytest

PRECISIONS = [6, 18]  # Last one is the pooltoken
BASE_PRECISIONS = [18, 6, 6]  # Token precisions of the base pool

N_COINS = len(PRECISIONS)
N_BASE_COINS = len(BASE_PRECISIONS)


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
def base_coins(ERC20Mock, alice):
    coins = []

    for i in range(N_BASE_COINS):
        coin = ERC20Mock.deploy(f"Base Coin {i}", f"B{i}", PRECISIONS[i], {'from': alice})
        coins.append(coin)

    yield coins


@pytest.fixture(scope="module")
def base_pool_token(CurveToken, alice):
    yield CurveToken.deploy(f"Stableswap Base", "BASE", 18, 0, {'from': alice})


@pytest.fixture(scope="module")
def coins(ERC20Mock, alice, base_pool_token):
    coins = []

    for i in range(N_COINS - 1):
        coin = ERC20Mock.deploy(f"Coin {i}", f"C{i}", PRECISIONS[i], {'from': alice})
        coins.append(coin)

    coins.append(base_pool_token)

    yield coins


@pytest.fixture(scope="module")
def pool_token(CurveToken, alice):
    yield CurveToken.deploy(f"Stableswap", "STBL", 18, 0, {'from': alice})


@pytest.fixture(scope="module")
def base_swap(StableSwap, alice, base_coins, base_pool_token):
    # Deploy the pool
    contract = StableSwap.deploy(alice, base_coins, base_pool_token, 100, 0, 0, {'from': alice})
    base_pool_token.set_minter(contract, {'from': alice})

    # Deposit $1M of every coin
    initial_amounts = [10 ** (j + 6) for j in BASE_PRECISIONS]
    for coin, amount in zip(base_coins, initial_amounts):
        coin._mint_for_testing(alice, amount, {'from': alice})
    coin.approve(contract, 2**256-1, {'from': alice})
    contract.add_liquidity(initial_amounts, 0, {'from': alice})

    yield contract


@pytest.fixture(scope="module")
def swap(StableSwap, alice, coins, pool_token, base_swap):
    contract = StableSwap.deploy(alice, coins, pool_token, base_swap, 100, 0, 0, {'from': alice})
    pool_token.set_minter(contract, {'from': alice})

    yield contract


def approx(a, b, precision=1e-10):
    return 2 * abs(a - b) / (a + b) <= precision
