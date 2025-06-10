import json
import os
from dotenv import load_dotenv

from brownie import accounts
from brownie.project import load as load_project
from brownie.project.main import get_loaded_projects
from brownie import network

load_dotenv()

# set a throwaway admin account here
deployer_pk = os.getenv('DEPLOYER_PK')

DEPLOYER = accounts.add(deployer_pk)
REQUIRED_CONFIRMATIONS = 1

# deployment settings
# most settings are taken from `contracts/pools/{POOL_NAME}/pooldata.json`
POOL_NAME = "ZRC20"

# temporary owner address
POOL_OWNER = "0x19caCb4c0A7fC25598CC44564ED0eCA01249fc31"
# GAUGE_OWNER = "0xedf2c58e16cc606da1977e79e1e69e79c54fe242"

# MINTER = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"


def _tx_params():
    return {
        # "gas": 12000000,
        "from": DEPLOYER,
        "gasPrice": 8000000000,  # Optional: Adjust gas price if needed
    }


def main():
    print(network.show_active())  # Shows the active network
    print(network.chain.id)

    project = get_loaded_projects()[0]
    balance = DEPLOYER.balance()

    print(f"Deployer address: {DEPLOYER}")
    print(f"Deployer balance: {balance / 1e18:.4f} ETH")

    # load data about the deployment from `pooldata.json`
    contracts_path = project._path.joinpath("contracts/pools")
    with contracts_path.joinpath(f"{POOL_NAME}/pooldata.json").open() as fp:
        pool_data = json.load(fp)

    swap_name = next(i.stem for i in contracts_path.glob(f"{POOL_NAME}/StableSwap*"))
    swap_deployer = getattr(project, swap_name)
    token_deployer = getattr(project, pool_data.get("lp_contract"))

    underlying_coins = [i["underlying_address"] for i in pool_data["coins"]]
    wrapped_coins = [i.get("wrapped_address", i["underlying_address"]) for i in pool_data["coins"]]

    base_pool = None
    if "base_pool" in pool_data:
        with contracts_path.joinpath(f"{pool_data['base_pool']}/pooldata.json").open() as fp:
            base_pool_data = json.load(fp)
            base_pool = base_pool_data["swap_address"]

    # deploy the token
    decimals = 18
    total_supply = 0
    token_args = pool_data["lp_constructor"]

    token = token_deployer.deploy(
        token_args["name"],
        token_args["symbol"],
        decimals,
        total_supply,
        _tx_params(),
    )

    # deploy the pool
    abi = next(i["inputs"] for i in swap_deployer.abi if i["type"] == "constructor")
    args = pool_data["swap_constructor"]
    args.update(
        _coins=wrapped_coins,
        _underlying_coins=underlying_coins,
        _pool_token=token,
        _base_pool=base_pool,
        _owner=POOL_OWNER,
    )
    deployment_args = [args[i["name"]] for i in abi] + [_tx_params()]

    swap = swap_deployer.deploy(*deployment_args)

    # set the minter
    token.set_minter(swap, _tx_params())

    # @dev: not working, check why
    # deploy the liquidity gauge
    # LiquidityGaugeV3 = load_project("curvefi/curve-dao-contracts@1.2.0").LiquidityGaugeV3
    # LiquidityGaugeV3.deploy(token, MINTER, GAUGE_OWNER, _tx_params())

    # deploy the zap
    zap_name = next((i.stem for i in contracts_path.glob(f"{POOL_NAME}/Deposit*")), None)
    if zap_name is not None:
        zap_deployer = getattr(project, zap_name)
        abi = next(i["inputs"] for i in zap_deployer.abi if i["type"] == "constructor")
        args = {
            "_coins": wrapped_coins,
            "_underlying_coins": underlying_coins,
            "_token": token,
            "_pool": swap,
            "_curve": swap,
        }
        deployment_args = [args[i["name"]] for i in abi] + [_tx_params()]
        zap_deployer.deploy(*deployment_args)

    # deploy the rate calculator
    rate_calc_name = next(
        (i.stem for i in contracts_path.glob(f"{POOL_NAME}/RateCalculator*")), None
    )
    if rate_calc_name is not None:
        rate_calc_deployer = getattr(project, rate_calc_name)
        rate_calc_deployer.deploy(_tx_params())

    print(f"Gas used in deployment: {(balance - DEPLOYER.balance()) / 1e18:.4f} ETH")
