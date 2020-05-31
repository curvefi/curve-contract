import pytest

N_COINS = 3
UP = [8, 18, 8]  # Ren/h/w, for example - why not
UU = [10 ** p for p in UP]
c_rates = [10 ** 18] * 3
use_lending = [True, False, False]
tethered = [False, False, False]
PRECISIONS = [10 ** 18 // u for u in UU]
MAX_UINT = 2 ** 256 - 1


@pytest.fixture(autouse=True)
def isolation_setup(fn_isolation):
    pass


@pytest.fixture(scope="module")
def coins(ERC20, accounts):
    coins = []

    for i in range(N_COINS):
        coin = ERC20.deploy(f"Coin {i}", f"C{i}", UP[i], 10**12, {'from': accounts[0]})
        coins.append(coin)

    yield coins


@pytest.fixture(scope="module")
def pool_token(ERC20, accounts):
    yield ERC20.deploy(f"Stableswap", "STBL", 18, 0, {'from': accounts[0]})


@pytest.fixture(scope="module")
def cerc20s(Mock_cERC20, accounts, coins):
    c_coins = coins.copy()
    for i in range(N_COINS):
        if not use_lending[i]:
            continue
        c_coin = Mock_cERC20.deploy(f"C-Coin {i}", f"C{i}", 18, 0, coins[i], c_rates[i], {'from': accounts[0]})
        coins[i].transfer(c_coin, 10 ** 11 * UU[i], {'from': accounts[0]})
        c_coins[i] = c_coin

    yield c_coins


@pytest.fixture(scope="module")
def swap(StableSwap, accounts, coins, cerc20s, pool_token):
    contract = StableSwap.deploy(cerc20s, pool_token, 360 * 2, 10**7, {'from': accounts[0]})
    pool_token.set_minter(contract, {'from': accounts[0]})

    yield contract


def approx(a, b, precision=1e-10):
    return 2 * abs(a - b) / (a + b) <= precision
