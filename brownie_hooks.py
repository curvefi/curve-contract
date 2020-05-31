from deploy_config_renbtc import (
        COINS, SWAP_DEPLOY_ADDRESS,
        PRECISIONS, USE_LENDING)

N_COINS = len(COINS)

replacements={
    '___N_COINS___': str(N_COINS),
    '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']',
    '___PRECISION_MUL___': '[' + ', '.join(
        'convert(%s, uint256)' % (10 ** 18 // i) for i in PRECISIONS) + ']',
    '___USE_LENDING___': '[' + ', '.join(
            str(i) for i in USE_LENDING) + ']',
}


def brownie_load_source(path, source):
    if path.stem == "StableSwap":
        for k, v in replacements.items():
            source = source.replace(k, v)

    return source
