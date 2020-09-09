import json
from brownie import accounts, chain, CurvePool

from . import deployment_config as config


POOLS = [
    '0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56',
    '0x52EA46506B9CC5Ef470C5bf89f17Dc28bB35D85C',
    '0x45F783CCE6B7FF23B2ab2D70e416cdb7D6055f51',
    '0x79a8C46DeA5aDa233ABaFFD40F3A0A2B1e5A4F27',
    '0xA5407eAE9Ba41422680e2e00537571bcC53efBfD',
    '0x06364f10B501e868329afBc005b3492902d6C763',
    '0x93054188d876f558f4a66B2EF1d97d16eDf0895B',
    '0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714',
]


def live():
    admin = accounts.at("0xC447FcAF1dEf19A583F97b3620627BF69c05b5fB")
    with open(config.DEPLOYMENTS_JSON) as fp:
        pool_proxy = json.load(fp)['PoolProxy']

    transfer_ownership(admin, pool_proxy, config.REQUIRED_CONFIRMATIONS)


def development():
    # only works on a forked mainnet
    admin = accounts.at("0xC447FcAF1dEf19A583F97b3620627BF69c05b5fB")
    new_admin = "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"

    transfer_ownership(admin, new_admin, 1)
    chain.sleep(86400 * 3 + 1)
    transfer_ownership(admin, new_admin, 1)
    sanity_check(new_admin)


def transfer_ownership(admin, new_admin, confs):
    for addr in POOLS:
        contract = CurvePool.at(addr)

        if contract.owner() != admin:
            print(f"ERROR: {admin} is not the owner of {addr}")
            continue

        deadline = contract.transfer_ownership_deadline()

        if deadline == 0:
            contract.commit_transfer_ownership(new_admin, {'from': admin})
            print(f"SUCCESS: Ownership transfer of {addr} has been initiated")
        elif deadline < chain.time():
            contract.apply_transfer_ownership({'from': admin})
            print(f"SUCCESS: Ownership transfer of {addr} is complete")
        else:
            print(
                f"ERROR: Transfer deadline for {addr} not passed, you must "
                f"wait another {deadline - chain.time()} seconds"
            )


def sanity_check(owner):
    for addr in POOLS:
        contract = CurvePool.at(addr)

        if contract.owner() != owner:
            raise ValueError(f"Unexpected owner for {addr}")
