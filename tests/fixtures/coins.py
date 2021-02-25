import pytest
from brownie import ETH_ADDRESS, ZERO_ADDRESS, ERC20Mock, ERC20MockNoReturn
from brownie_tokens import MintableForkToken
from conftest import WRAPPED_COIN_METHODS

# public fixtures - these can be used when testing


@pytest.fixture(scope="module")
def wrapped_coins(project, alice, pool_data, _underlying_coins, is_forked, aave_lending_pool):
    return _wrapped(project, alice, pool_data, _underlying_coins, is_forked, aave_lending_pool)


@pytest.fixture(scope="module")
def underlying_coins(_underlying_coins, _base_coins):
    if _base_coins:
        return _underlying_coins[:1] + _base_coins
    else:
        return _underlying_coins


@pytest.fixture(scope="module")
def pool_token(project, alice, pool_data):
    return _pool_token(project, alice, pool_data)


@pytest.fixture(scope="module")
def base_pool_token(project, charlie, base_pool_data, is_forked):
    if base_pool_data is None:
        return
    if is_forked:
        return _MintableTestToken(base_pool_data["lp_token_address"], base_pool_data)

    # we do some voodoo here to make the base LP tokens work like test ERC20's
    # charlie is the initial liquidity provider, he starts with the full balance
    def _mint_for_testing(target, amount, tx=None):
        token.transfer(target, amount, {"from": charlie})

    token = _pool_token(project, charlie, base_pool_data)
    token._mint_for_testing = _mint_for_testing
    return token


# private API below


class _MintableTestToken(MintableForkToken):
    def __init__(self, address, pool_data=None):
        super().__init__(address)

        # standardize mint / rate methods
        if pool_data is not None and "wrapped_contract" in pool_data:
            fn_names = WRAPPED_COIN_METHODS[pool_data["wrapped_contract"]]
            for target, attr in fn_names.items():
                if hasattr(self, attr) and target != attr:
                    setattr(self, target, getattr(self, attr))


def _deploy_wrapped(project, alice, pool_data, idx, underlying, aave_lending_pool):
    coin_data = pool_data["coins"][idx]
    fn_names = WRAPPED_COIN_METHODS[pool_data["wrapped_contract"]]
    deployer = getattr(project, pool_data["wrapped_contract"])

    decimals = coin_data["wrapped_decimals"]
    name = coin_data.get("name", f"Coin {idx}")
    symbol = coin_data.get("name", f"C{idx}")

    if pool_data["wrapped_contract"] == "ATokenMock":
        contract = deployer.deploy(
            name, symbol, decimals, underlying, aave_lending_pool, {"from": alice}
        )
    else:
        contract = deployer.deploy(name, symbol, decimals, underlying, {"from": alice})

    for target, attr in fn_names.items():
        if target != attr:
            setattr(contract, target, getattr(contract, attr))
    if coin_data.get("withdrawal_fee"):
        contract._set_withdrawal_fee(coin_data["withdrawal_fee"], {"from": alice})

    return contract


def _wrapped(project, alice, pool_data, underlying_coins, is_forked, aave_lending_pool):
    coins = []

    if not pool_data.get("wrapped_contract"):
        return underlying_coins

    if is_forked:
        for i, coin_data in enumerate(pool_data["coins"]):
            if not coin_data.get("wrapped_decimals"):
                coins.append(underlying_coins[i])
            else:
                coins.append(_MintableTestToken(coin_data["wrapped_address"], pool_data))
        return coins

    for i, coin_data in enumerate(pool_data["coins"]):
        underlying = underlying_coins[i]
        if not coin_data.get("wrapped_decimals") or not coin_data.get("decimals"):
            coins.append(underlying)
        else:
            contract = _deploy_wrapped(project, alice, pool_data, i, underlying, aave_lending_pool)
            coins.append(contract)
    return coins


def _underlying(alice, project, pool_data, is_forked, base_pool_token):
    coins = []

    if is_forked:
        for data in pool_data["coins"]:
            if data.get("underlying_address") == ETH_ADDRESS:
                coins.append(ETH_ADDRESS)
            else:
                coins.append(
                    _MintableTestToken(
                        data.get("underlying_address", data.get("wrapped_address")), pool_data
                    )
                )
    else:
        for i, coin_data in enumerate(pool_data["coins"]):
            if coin_data.get("underlying_address") == ETH_ADDRESS:
                coins.append(ETH_ADDRESS)
                continue
            if coin_data.get("base_pool_token"):
                coins.append(base_pool_token)
                continue
            if not coin_data.get("decimals"):
                contract = _deploy_wrapped(project, alice, pool_data, i, ZERO_ADDRESS, ZERO_ADDRESS)
            else:
                decimals = coin_data["decimals"]
                deployer = ERC20MockNoReturn if coin_data["tethered"] else ERC20Mock
                contract = deployer.deploy(
                    f"Underlying Coin {i}", f"UC{i}", decimals, {"from": alice}
                )
            coins.append(contract)

    return coins


def _pool_token(project, alice, pool_data):
    name = pool_data["name"]
    deployer = getattr(project, pool_data["lp_contract"])
    args = [f"Curve {name} LP Token", f"{name}CRV", 18, 0][: len(deployer.deploy.abi["inputs"])]
    return deployer.deploy(*args, {"from": alice})


# private fixtures used for setup in other fixtures - do not use in tests!


@pytest.fixture(scope="module")
def _underlying_coins(
    alice, project, pool_data, is_forked, base_pool_token, _add_base_pool_liquidity
):
    return _underlying(alice, project, pool_data, is_forked, base_pool_token)


@pytest.fixture(scope="module")
def _base_coins(alice, project, base_pool_data, is_forked):
    if base_pool_data is None:
        return []
    return _underlying(alice, project, base_pool_data, is_forked, None)
