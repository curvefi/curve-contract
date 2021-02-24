import pytest
import requests
from brownie import ETH_ADDRESS, ZERO_ADDRESS, Contract, ERC20Mock, ERC20MockNoReturn
from brownie.convert import to_address

from conftest import WRAPPED_COIN_METHODS

_holders = {}


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


class _MintableTestToken(Contract):
    def __init__(self, address, pool_data=None):
        super().__init__(address)

        # standardize mint / rate methods
        if pool_data is not None and "wrapped_contract" in pool_data:
            fn_names = WRAPPED_COIN_METHODS[pool_data["wrapped_contract"]]
            for target, attr in fn_names.items():
                if hasattr(self, attr) and target != attr:
                    setattr(self, target, getattr(self, attr))

        # get top token holder addresses
        address = self.address
        if address not in _holders:
            holders = requests.get(
                f"https://api.ethplorer.io/getTopTokenHolders/{address}",
                params={"apiKey": "freekey", "limit": 50},
            ).json()
            _holders[address] = [to_address(i["address"]) for i in holders["holders"]]

    def _mint_for_testing(self, target, amount, tx=None):
        if self.address == "0x674C6Ad92Fd080e4004b2312b45f796a192D27a0":
            # USDN
            self.deposit(target, amount, {"from": "0x90f85042533F11b362769ea9beE20334584Dcd7D"})
            return
        if self.address == "0x0E2EC54fC0B509F445631Bf4b91AB8168230C752":
            # LinkUSD
            self.mint(target, amount, {"from": "0x62F31E08e279f3091d9755a09914DF97554eAe0b"})
            return
        if self.address == "0x196f4727526eA7FB1e17b2071B3d8eAA38486988":
            # RSV
            self.changeMaxSupply(2 ** 128, {"from": self.owner()})
            self.mint(target, amount, {"from": self.minter()})
            return
        if self.address == "0x5228a22e72ccC52d415EcFd199F99D0665E7733b":
            # pBTC
            self.mint(target, amount, {"from": self.pNetwork()})
            return
        if self.name().startswith("Aave"):
            underlying = _MintableTestToken(self.UNDERLYING_ASSET_ADDRESS())
            lending_pool = Contract("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9")
            underlying._mint_for_testing(target, amount)
            underlying.approve(lending_pool, amount, {"from": target})
            lending_pool.deposit(underlying, amount, target, 0, {"from": target})
            return
        if self.address == "0x4A64515E5E1d1073e83f30cB97BEd20400b66E10":
            # wZEC
            self.mint(target, amount, {"from": "0x5Ca1262e25A5Fb6CA8d74850Da2753f0c896e16c"})
            return
        if self.address == "0x1C5db575E2Ff833E46a2E9864C22F4B22E0B37C2":
            # renZEC
            self.mint(target, amount, {"from": "0xc3BbD5aDb611dd74eCa6123F05B18acc886e122D"})
            return

        for address in _holders[self.address].copy():
            if address == self.address:
                # don't claim from the treasury - that could cause wierdness
                continue
            balance = self.balanceOf(address)
            try:
                if amount > balance:
                    self.transfer(target, balance, {"from": address})
                    amount -= balance
                else:
                    self.transfer(target, amount, {"from": address})
                    return
            except Exception:
                # sometimes tokens just don't want to be stolen
                pass

        raise ValueError(f"Insufficient tokens available to mint {self.name()}")


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
