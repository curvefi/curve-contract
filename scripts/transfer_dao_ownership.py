import json
from brownie import ERC20CRV, GaugeController, PoolProxy, VotingEscrow

from . import deployment_config as config


def live():
    admin, _ = config.get_live_admin()
    with open(config.DEPLOYMENTS_JSON) as fp:
        deployments = json.load(fp)

    transfer_ownership(
        admin,
        config.ARAGON_AGENT,
        deployments['GaugeController'],
        deployments['VotingEscrow'],
        deployments['PoolProxy'],
        deployments['ERC20CRV'],
        config.REQUIRED_CONFIRMATIONS
    )


def development():
    #  only works on a forked mainnet after the previous stages have been completed
    admin, _ = config.get_live_admin()
    with open(config.DEPLOYMENTS_JSON) as fp:
        deployments = json.load(fp)

    transfer_ownership(
        admin,
        config.ARAGON_AGENT,
        deployments['GaugeController'],
        deployments['VotingEscrow'],
        deployments['PoolProxy'],
        deployments['ERC20CRV']
    )


def transfer_ownership(admin, new_admin, gauge_controller, voting_escrow, pool_proxy, erc20crv, confs=1):
    gauge_controller = GaugeController.at(gauge_controller)
    voting_escrow = VotingEscrow.at(voting_escrow)
    pool_proxy = PoolProxy.at(pool_proxy)
    erc20crv = ERC20CRV.at(erc20crv)

    gauge_controller.commit_transfer_ownership(new_admin, {'from': admin, 'required_confs': confs})
    gauge_controller.apply_transfer_ownership({'from': admin, 'required_confs': confs})

    voting_escrow.commit_transfer_ownership(new_admin, {'from': admin, 'required_confs': confs})
    voting_escrow.apply_transfer_ownership({'from': admin, 'required_confs': confs})

    pool_proxy.commit_set_admins(
        new_admin, new_admin, new_admin, {'from': admin, 'required_confs': confs}
    )
    pool_proxy.apply_set_admins({'from': admin, 'required_confs': confs})

    erc20crv.set_admin(new_admin, {'from': admin, 'required_confs': confs})
