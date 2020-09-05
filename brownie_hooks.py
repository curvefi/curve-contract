
N_COINS = 3  # DAI, USDC, USDT
PRECISIONS = [18, 6, 6]
PRECISION_MUL = [10**18 // (10**i) for i in PRECISIONS]
RATES = [i*10**18 for i in PRECISION_MUL]

replacements = {
    '___N_COINS___': str(N_COINS),
    '___PRECISION_MUL___': str(PRECISION_MUL),
    '___RATES___': str(RATES),
    '___FEE_INDEX___': str(2)
}


def brownie_load_source(path, source):
    if path.stem in ("StableSwap",):
        for k, v in replacements.items():
            source = source.replace(k, v)

    return source
