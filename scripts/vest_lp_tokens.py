import json
import threading
from decimal import Decimal
from brownie import accounts, history, ERC20CRV, VestingEscrow

from . import deployment_config as config

TOTAL_AMOUNT = 151515151515151515151515151
VESTING_PERIOD = 86400 * 365

# burn addresses / known scammers
BLACKLIST = [
    "0x000000000000000000000000000000000000dead",
    "0xe857656b7804ecc0d0d0fd643c6cfb69063a7d1a",
    "0xbce6d09b800d0bc03f34ef93ed356519faec64d0",
    "0xe4ffd96b5e6d2b6cdb91030c48cc932756c951b5"
]


def live():
    """
    Vest tokens in a live environment.

    * Apply web3 gas price strategy and middlewares
    * Run main deployment and distribution logic
    """
    admin, funding_admins = config.get_live_admin()

    with open(config.DEPLOYMENTS_JSON) as fp:
        deployments = json.load(fp)

    vest_tokens(
        admin,
        funding_admins,
        deployments['ERC20CRV'],
        config.REQUIRED_CONFIRMATIONS
    )


def development():
    """
    Vest tokens in a development environment.

    * Deploy the DAO token
    * Run the main deployment and distribution logic
    * Perform a sanity check to confirm balances and total supply are as expected
    """
    token = ERC20CRV.deploy("Curve DAO Token", "CRV", 18, {'from': accounts[0]})
    vesting_escrow, vested_amounts = vest_tokens(accounts[0], accounts[1:5], token, 1)
    sanity_check(vesting_escrow, vested_amounts)


logging_lock = threading.Lock()
logger_data = []


def _log_tx(**kwargs):
    with logging_lock:
        logger_data.append(kwargs)
        with open("vesting-lp-log.json", "w") as fp:
            json.dump(logger_data, fp)


def _fund_accounts(acct, vesting_escrow, fund_arguments, confs):
    # called with 5 threads to fund recipients more efficiently
    while fund_arguments:
        try:
            recipients, amounts = fund_arguments.pop()
        except IndexError:
            break
        tx = vesting_escrow.fund(recipients, amounts, {'from': acct, 'required_confs': 0})
        _log_tx(
            txid=tx.txid,
            fn_name=tx.fn_name,
            recipients=recipients,
            amounts=amounts,
            sender=acct.address
        )
        tx.wait(confs)


def vest_tokens(admin, funding_admins, token_address, confs):
    start_idx = len(history)

    # get token Contract object
    token = ERC20CRV.at(token_address)

    # deploy vesting contract
    start_time = token.future_epoch_time_write.call()

    vesting_escrow = VestingEscrow.deploy(
        token,
        start_time,
        start_time + VESTING_PERIOD,
        False,
        funding_admins,
        {'from': admin, 'required_confs': confs}
    )
    _log_tx(
        txid=vesting_escrow.tx.txid,
        fn_name="VestingEscrow.deploy",
        contract_address=vesting_escrow.address
    )

    # load vesting data from json
    with open(config.LP_VESTING_JSON) as fp:
        vested_pct = {k.lower(): Decimal(v) for k, v in json.load(fp).items()}

    for addr in BLACKLIST:
        if addr.lower() in vested_pct:
            del vested_pct[addr]

    # calculate absolute amounts to be distributed
    initial_total = sum(int(v * TOTAL_AMOUNT) for v in vested_pct.values())
    adjustment_pct = Decimal(TOTAL_AMOUNT) / initial_total
    vested_amounts = sorted(
        ([k, int(v * TOTAL_AMOUNT * adjustment_pct)] for k, v in vested_pct.items()),
        key=lambda k: k[1],
        reverse=True,
    )

    if vested_amounts[-1][1] < 0:
        raise ValueError(f"'{config.LP_VESTING_JSON}' contains negative amounts!")

    vested_amounts = [i for i in vested_amounts if i[1]]

    # floats -> int, we expect to be ever so slightly over, so lets fix that
    final_total = sum(i[1] for i in vested_amounts)

    if not 0 < abs(final_total - TOTAL_AMOUNT) < len(vested_amounts):
        raise ValueError("Imprecision!!! Distribution amounts are too far off!")

    for i in range(abs(final_total - TOTAL_AMOUNT)):
        if final_total < TOTAL_AMOUNT:
            vested_amounts[i][1] += 1
        else:
            vested_amounts[i][1] -= 1

    tx = token.approve(vesting_escrow, TOTAL_AMOUNT, {'from': admin, 'required_confs': confs})
    _log_tx(
        txid=tx.txid,
        fn_name=tx.fn_name,
        spender=vesting_escrow.address,
        amount=TOTAL_AMOUNT,
    )
    tx = vesting_escrow.add_tokens(TOTAL_AMOUNT, {'from': admin, 'required_confs': confs})
    _log_tx(
        txid=tx.txid,
        fn_name=tx.fn_name,
        amount=TOTAL_AMOUNT,
    )

    # convert vested_amounts into input args for `VestingEscrow.fund` calls
    fund_arguments = [
        ([x[0] for x in vested_amounts[i:i+100]], [x[1] for x in vested_amounts[i:i+100]])
        for i in range(0, len(vested_amounts), 100)
    ]

    # final call needs to be extended with zero values
    zeros = 100 - len(fund_arguments[-1][0])
    fund_arguments[-1] = (
        fund_arguments[-1][0] + ["0x0000000000000000000000000000000000000000"] * zeros,
        fund_arguments[-1][1] + [0] * zeros
    )

    # use threading to handle the funding across several accounts
    funding_threads = []
    for acct in [admin] + funding_admins:
        thread = threading.Thread(
            target=_fund_accounts,
            args=(acct, vesting_escrow, fund_arguments, confs),
        )
        funding_threads.append(thread)
        thread.start()

    for thread in funding_threads:
        thread.join()

    # burn all the admin accounts!
    tx = vesting_escrow.disable_fund_admins({'from': admin, 'required_confs': confs})
    _log_tx(
        txid=tx.txid,
        fn_name=tx.fn_name,
    )
    vesting_escrow.commit_transfer_ownership(
        "0x000000000000000000000000000000000000dead",
        {'from': admin, 'required_confs': confs}
    )
    _log_tx(
        txid=tx.txid,
        fn_name=tx.fn_name,
    )
    vesting_escrow.apply_transfer_ownership({'from': admin, 'required_confs': confs})
    _log_tx(
        txid=tx.txid,
        fn_name=tx.fn_name,
    )

    gas_used = sum(i.gas_used for i in history[start_idx:])
    print(f"Distribution complete! Total gas used: {gas_used}")

    # return the final vested amounts to be used in `sanity_check`, if desired
    return vesting_escrow, vested_amounts


def sanity_check(vesting_address, vested_amounts):
    vesting_escrow = VestingEscrow.at(vesting_address)

    if vesting_escrow.initial_locked_supply() != TOTAL_AMOUNT:
        raise ValueError(f"Unexpected locked supply: {vesting_escrow.initial_locked_supply()}")
    if vesting_escrow.unallocated_supply() != 0:
        raise ValueError(f"Unallocated supply remains: {vesting_escrow.unallocated_supply()}")

    for count, (acct, expected) in enumerate(vested_amounts, start=1):
        balance = vesting_escrow.initial_locked(acct)
        if balance != expected:
            raise ValueError(
                f"Incorrect vested amount for {acct} - expected {expected}, got {balance}"
            )
        if not count % 250:
            print(f"{count}/{len(vested_amounts)} balances verified...")

    print("Sanity check passed!")
