
N_COINS = 2  # hBTC, wBTC
PRECISIONS = [18, 8]
PRECISION_MUL = [10**18 // (10**i) for i in PRECISIONS]
RATES = [i*10**18 for i in PRECISION_MUL]

replacements = {
    '___N_COINS___': str(N_COINS),
    '___PRECISION_MUL___': str(PRECISION_MUL),
    '___RATES___': str(RATES),
}


def brownie_load_source(path, source):
    if path.stem in ("StableSwap",):
        for k, v in replacements.items():
            source = source.replace(k, v)

    return source
