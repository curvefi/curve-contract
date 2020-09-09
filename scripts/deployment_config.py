"""
Deployment Configuration file
=============================
This script holds customizeable / sensetive values related to the DAO deployment scripts.
See `README.md` in this directory for more information on how deployment works.
"""

from brownie import accounts, rpc, web3
from web3 import middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy as gas_strategy

LP_VESTING_JSON = "scripts/early-users.json"
DEPLOYMENTS_JSON = "deployments.json"
REQUIRED_CONFIRMATIONS = 3

# Aragon agent address - set after the Aragon DAO is deployed
ARAGON_AGENT = None

YEAR = 86400 * 365

# `VestingEscrow` contracts to be deployed
STANDARD_ESCROWS = [
    {  # Founder
        'duration': 4 * YEAR,
        'can_disable': False,
        'admin': "0x000000000000000000000000000000000000dead",
        'recipients': {
            '0x7a16fF8270133F063aAb6C9977183D9e72835428': 200_240288341358467370146501,
            '0xF89501B77b2FA6329F94F5A05FE84cEbb5c8b1a0': 200_240288341358467370146501,
            '0x9B44473E223f8a3c047AD86f387B80402536B029': 200_240288341358467370146501,
            '0x32D03DB62e464c9168e41028FFa6E9a05D8C6451': 200_240288341358467370146501
        },
    },
    {  # Investors
        'duration': 2 * YEAR,
        'can_disable': False,
        'admin': "0x000000000000000000000000000000000000dead",
        'recipients': {
            '0x39362B3CA91D40Aff08EbcCbdd121090F3BB3Ef3': 16_019223067308677389611720,
            '0xd4A39d219ADB43aB00739DC5D876D98Fdf0121Bf': 56_067280735580370863641020,
            '0x279a7DBFaE376427FFac52fcb0883147D42165FF': 16_019223067308677389611720,
            '0x394A16eeA604fBD86B0b45184b2d790c83a950E3': 4_004805766827169347402930,
        },
    },
    {  # Advisors and partners with known addresses
        'duration': 2 * YEAR,
        'can_disable': True,
        'admin': '0x39415255619783A2E71fcF7d8f708A951d92e1b6',  # Curve
        'recipients': {
            '0xeBC551A91D951875e570da49541d5a8bED469cF8': 2_002402883413584673701465,
        }
    },
    {  # Employees
        'duration': 2 * YEAR,
        'can_disable': True,
        'admin': '0x39415255619783A2E71fcF7d8f708A951d92e1b6',  # Curve
        'recipients': {
            '0xBe286d574b1Ea46f54955Bd856821f84DFd20b2e': 30_303030302325581395348837,
            '0x825AA4A8F72ab6AE0C55D840759711bBe00a9304': 15_151515151162790697674418,
            '0x94dFcE828c3DAaF6492f1B6F66f9a1825254D24B': 7_878787878604651162790697,
            '0x6632EdA2685EABFb7B3B45669CFa5441349485d3': 3_030303030232558139534883,
            '0x0Ac51a4E170bF73e7ac54283E61C9717EAc2A241': 7_878787878604651162790697,
        }
    }
]

# `VestingEscrowFactory` contracts to be deployed
FACTORY_ESCROWS = [
    {  # Advisors with unknown addresses
        'admin': "0x39415255619783A2E71fcF7d8f708A951d92e1b6",  # Curve
        'amount': 14_016820183895092715910255
    },
    {  # Rest of employee coins
        'admin': "0x39415255619783A2E71fcF7d8f708A951d92e1b6",  # Curve
        'amount': 26_666666666046511627906979
    },
    {  # Community fund
        'admin': "0x000000000000000000000000000000000000dead",  # set to DAO  XXX
        'amount': 151_515151511627906976744186
    },
]


def get_live_admin():
    # Admin and funding admin account objects used for in a live environment
    # May be created via accounts.load(name) or accounts.add(privkey)
    # https://eth-brownie.readthedocs.io/en/stable/account-management.html
    admin = None  #
    funding_admins = [None, None, None, None]
    return admin, funding_admins


if not rpc.is_active():
    # logic that only executes in a live environment
    web3.eth.setGasPriceStrategy(gas_strategy)
    web3.middleware_onion.add(middleware.time_based_cache_middleware)
    web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
    web3.middleware_onion.add(middleware.simple_cache_middleware)
