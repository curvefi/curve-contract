import json

from brownie import accounts
from brownie.project.main import get_loaded_projects
from brownie.network.gas.strategies import GasNowScalingStrategy

# modify this import if you wish to deploy a different liquidity gauge
from brownie import LiquidityGauge as LiquidityGauge

# set a throwaway admin account here
DEPLOYER = accounts.add()
REQUIRED_CONFIRMATIONS = 1

# deployment settings
# most settings are taken from `contracts/pools/{POOL_NAME}/pooldata.json`
POOL_NAME = ""
POOL_OWNER = "0xeCb456EA5365865EbAb8a2661B0c503410e9B347"  # PoolProxy
MINTER = "0xd061D61a4d941c39E5453435B6345Dc261C2fcE0"


def _tx_params():
    return {
        'from': DEPLOYER,
        'required_confs': REQUIRED_CONFIRMATIONS,
        'gas_price': GasNowScalingStrategy("standard", "fast"),
    }


def main():
    project = get_loaded_projects()[0]
    balance = DEPLOYER.balance()

    # load data about the deployment from `pooldata.json`
    contracts_path = project._path.joinpath("contracts/pools")
    with contracts_path.joinpath(f"{POOL_NAME}/pooldata.json").open() as fp:
        pool_data = json.load(fp)

    swap_name = next(i.stem for i in contracts_path.glob(f"{POOL_NAME}/StableSwap*"))
    swap_deployer = getattr(project, swap_name)
    token_deployer = getattr(project, pool_data.get('lp_contract'))

    underlying_coins = [i['underlying_address'] for i in pool_data['coins']]
    wrapped_coins = [i.get('wrapped_address', i['underlying_address']) for i in pool_data['coins']]

    base_pool = None
    if "base_pool" in pool_data:
        with contracts_path.joinpath(f"{pool_data['base_pool']}/pooldata.json").open() as fp:
            base_pool_data = json.load(fp)
            base_pool = base_pool_data['swap_address']

    # deploy the token
    token_args = pool_data["lp_constructor"]
    token = token_deployer.deploy(token_args['name'], token_args['symbol'], _tx_params())

    # deploy the pool
    abi = next(i['inputs'] for i in swap_deployer.abi if i['type'] == "constructor")
    args = pool_data["swap_constructor"]
    args.update(
        _coins=wrapped_coins,
        _underlying_coins=underlying_coins,
        _pool_token=token,
        _base_pool=base_pool,
        _owner=POOL_OWNER,
    )
    deployment_args = [args[i['name']] for i in abi] + [_tx_params()]

    swap = swap_deployer.deploy(*deployment_args)

    # set the minter
    token.set_minter(swap, _tx_params())

    # deploy the liquidity gauge
    LiquidityGauge.deploy(token, MINTER, POOL_OWNER, _tx_params())

    # deploy the zap
    zap_name = next((i.stem for i in contracts_path.glob(f"{POOL_NAME}/Deposit*")), None)
    if zap_name is not None:
        zap_deployer = getattr(project, zap_name)

        abi = next(i['inputs'] for i in zap_deployer.abi if i['type'] == "constructor")
        args = {
            '_coins': wrapped_coins,
            '_underlying_coins': underlying_coins,
            '_token': token,
            '_pool': swap,
            '_curve': swap,
        }
        deployment_args = [args[i['name']] for i in abi] + [_tx_params()]

        zap_deployer.deploy(*deployment_args)

    print(f'Gas used in deployment: {(balance - DEPLOYER.balance()) / 1e18:.4f} ETH')
