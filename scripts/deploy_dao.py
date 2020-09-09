import json
from brownie import (
    accounts,
    history,
    ERC20CRV,
    GaugeController,
    LiquidityGauge,
    LiquidityGaugeReward,
    Minter,
    PoolProxy,
    VotingEscrow,
)

from . import deployment_config as config

# TODO set weights!

# name, type weight
GAUGE_TYPES = [
    ("Liquidity", 10**18),
]

# lp token, gauge weight
POOL_TOKENS = {
    "Compound": ('0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2', 12),
    "USDT": ('0x9fC689CCaDa600B6DF723D9E47D84d76664a1F23', 0),
    "Y": ('0xdF5e0e81Dff6FAF3A7e52BA697820c5e32D806A8', 1446),
    "bUSD": ('0x3B3Ac5386837Dc563660FB6a0937DFAa5924333B', 2),
    "PAX": ('0xD905e2eaeBe188fc92179b6350807D8bd91Db0D8', 1),
    "RenBTC": ('0x49849C98ae39Fff122806C06791Fa73784FB3675', 26),
}

# lp token, reward contract, reward token, gauge weight
REWARD_POOL_TOKENS = {
    "sUSD": (
        '0xC25a3A3b969415c80451098fa907EC722572917F',
        '0xDCB6A51eA3CA5d3Fd898Fd6564757c7aAeC3ca92',  # Synthetix LP Rewards: sUSD
        '0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F',  # SNX
        472,
    ),
    "sBTC": (
        '0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3',
        "0x13C1542A468319688B89E323fe9A3Be3A90EBb27",  # Synthetix LP Rewards: sBTC
        '0x330416C863f2acCE7aF9C9314B422d24c672534a',  # BPT[SNX/REN]
        417,
    ),
}


def live_part_one():
    admin, _ = config.get_live_admin()
    deploy_part_one(admin, config.REQUIRED_CONFIRMATIONS, config.DEPLOYMENTS_JSON)


def live_part_two():
    admin, _ = config.get_live_admin()
    with open(config.DEPLOYMENTS_JSON) as fp:
        deployments = json.load(fp)
    token = ERC20CRV.at(deployments['ERC20CRV'])
    voting_escrow = VotingEscrow.at(deployments['VotingEscrow'])

    deploy_part_two(
        admin, token, voting_escrow, config.REQUIRED_CONFIRMATIONS, config.DEPLOYMENTS_JSON
    )


def development():
    token, voting_escrow = deploy_part_one(accounts[0])
    deploy_part_two(accounts[0], token, voting_escrow)


def deploy_part_one(admin, confs=1, deployments_json=None):
    token = ERC20CRV.deploy("Curve DAO Token", "CRV", 18, {'from': admin, 'required_confs': confs})
    voting_escrow = VotingEscrow.deploy(
        token, "Vote-escrowed CRV", "veCRV", "veCRV_1.0.0", {'from': admin, 'required_confs': confs}
    )
    deployments = {
        "ERC20CRV": token.address,
        "VotingEscrow": voting_escrow.address,
    }
    if deployments_json is not None:
        with open(deployments_json, 'w') as fp:
            json.dump(deployments, fp)
        print(f"Deployment addresses saved to {deployments_json}")

    return token, voting_escrow


def deploy_part_two(admin, token, voting_escrow, confs=1, deployments_json=None):
    gauge_controller = GaugeController.deploy(
        token, voting_escrow, {'from': admin, 'required_confs': confs}
    )
    for name, weight in GAUGE_TYPES:
        gauge_controller.add_type(name, weight, {'from': admin, 'required_confs': confs})

    pool_proxy = PoolProxy.deploy({'from': admin, 'required_confs': confs})
    minter = Minter.deploy(token, gauge_controller, {'from': admin, 'required_confs': confs})
    token.set_minter(minter, {'from': admin, 'required_confs': confs})

    deployments = {
        "ERC20CRV": token.address,
        "VotingEscrow": voting_escrow.address,
        "GaugeController": gauge_controller.address,
        "Minter": minter.address,
        "LiquidityGauge": {},
        "LiquidityGaugeReward": {},
        "PoolProxy": pool_proxy.address,
    }
    for name, (lp_token, weight) in POOL_TOKENS.items():
        gauge = LiquidityGauge.deploy(lp_token, minter, {'from': admin, 'required_confs': confs})
        gauge_controller.add_gauge(gauge, 0, weight, {'from': admin, 'required_confs': confs})
        deployments['LiquidityGauge'][name] = gauge.address

    for name, (lp_token, reward_claim, reward_token, weight) in REWARD_POOL_TOKENS.items():
        gauge = LiquidityGaugeReward.deploy(
            lp_token, minter, reward_claim, reward_token, {'from': admin, 'required_confs': confs}
        )
        gauge_controller.add_gauge(gauge, 0, weight, {'from': admin, 'required_confs': confs})
        deployments['LiquidityGaugeReward'][name] = gauge.address

    print(f"Deployment complete! Total gas used: {sum(i.gas_used for i in history)}")
    if deployments_json is not None:
        with open(deployments_json, 'w') as fp:
            json.dump(deployments, fp)
        print(f"Deployment addresses saved to {deployments_json}")
