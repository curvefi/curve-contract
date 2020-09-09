import json
from brownie import (
    accounts,
    ERC20CRV,
    VestingEscrow,
    VestingEscrowFactory,
    VestingEscrowSimple,
)

from . import deployment_config as config

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
YEAR = 86400 * 365


def live():
    """
    Vest tokens in a live environment.
    """
    admin, _ = config.get_live_admin()

    with open(config.DEPLOYMENTS_JSON) as fp:
        deployments = json.load(fp)

    vest_tokens(admin, deployments['ERC20CRV'], config.REQUIRED_CONFIRMATIONS)


def development():
    """
    Vest tokens in a development environment and validate the result.
    """
    token = ERC20CRV.deploy("Curve DAO Token", "CRV", 18, {'from': accounts[0]})
    vesting_escrow, vested_amounts = vest_tokens(accounts[0], token, 1)
    sanity_check(token, vesting_escrow, vested_amounts)


def vest_tokens(admin, token_address, confs):
    token = ERC20CRV.at(token_address)

    # deploy library and vesting factories
    target = VestingEscrowSimple.deploy({'from': admin, 'required_confs': confs})

    factory_contracts = []
    for data in config.FACTORY_ESCROWS:
        factory = VestingEscrowFactory.deploy(
            target, data['admin'], {'from': admin, 'required_confs': confs}
        )
        token.transfer(factory, data['amount'], {'from': admin, 'required_confs': confs})
        factory_contracts.append((factory, data['amount']))

    # deploy standard escrows
    start_time = token.future_epoch_time_write.call()
    for data in config.STANDARD_ESCROWS:

        vesting_escrow = VestingEscrow.deploy(
            token,
            start_time,
            start_time + data['duration'],
            data['can_disable'],
            [ZERO_ADDRESS] * 4,
            {'from': admin, 'required_confs': confs}
        )
        data['contract'] = vesting_escrow

        total_amount = sum(data['recipients'].values())
        token.approve(vesting_escrow, total_amount, {'from': admin, 'required_confs': confs})
        vesting_escrow.add_tokens(total_amount, {'from': admin, 'required_confs': confs})

        zeros = 100 - len(data['recipients'])
        fund_inputs = tuple(data['recipients'].items())
        recipients = [i[0] for i in fund_inputs] + [ZERO_ADDRESS] * zeros
        amounts = [i[1] for i in fund_inputs] + [0] * zeros

        vesting_escrow.fund(recipients, amounts, {'from': admin, 'required_confs': confs})

        if 'admin' in data:
            vesting_escrow.commit_transfer_ownership(
                data['admin'], {'from': admin, 'required_confs': confs}
            )
            vesting_escrow.apply_transfer_ownership({'from': admin, 'required_confs': confs})

    print("Deployments finished!\n\nFactories:")
    for factory, amount in factory_contracts:
        print(f"  {factory.address} : {amount} tokens")

    print("\nStandard Escrows:")
    for data in config.STANDARD_ESCROWS:
        total_amount = sum(data['recipients'].values())
        print(
            f"  {data['contract'].address}: {len(data['recipients'])} recipients, "
            f"{total_amount} total tokens, {data['duration']/YEAR} year lock"
        )

    return config.STANDARD_ESCROWS, factory_contracts


def sanity_check(token, standard_escrows, factory_escrows):

    for factory, amount in factory_escrows:
        if token.balanceOf(factory) != amount:
            raise ValueError(f"Incorrect balance in factory {factory.address}")

    for data in standard_escrows:
        escrow = data['contract']
        total_amount = sum(data['recipients'].values())
        if escrow.initial_locked_supply() != total_amount:
            raise ValueError(
                f"Unexpected locked supply in {escrow.address}: {escrow.initial_locked_supply()}"
            )
        if escrow.unallocated_supply() != 0:
            raise ValueError(
                f"Unallocated supply remains in {escrow.address}: {escrow.unallocated_supply()}"
            )

        for recipient, expected in data['recipients'].items():
            balance = escrow.initial_locked(recipient)
            if balance != expected:
                raise ValueError(
                    f"Incorrect vested amount for {recipient} in {escrow.address} "
                    f"- expected {expected}, got {balance}"
                )

    print("Sanity check passed!")
