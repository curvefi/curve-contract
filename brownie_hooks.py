
N_COINS = 2  # ?USD, BASE
PRECISIONS = [6, 18]
PRECISION_MUL = [10**18 // (10**i) for i in PRECISIONS]
RATES = [i*10**18 for i in PRECISION_MUL]

replacements = {
    '___N_COINS___': str(N_COINS),
    '___PRECISION_MUL___': str(PRECISION_MUL),
    '___RATES___': str(RATES),
    '___BASE_N_COINS___': '3',
    '___BASE_PRECISION_MUL___': str([1, 10**12, 10**12]),
    '___BASE_RATES___': str([10**18, 10**30, 10**30])
}


def brownie_load_source(path, source):
    if path.stem in ("StableSwap", "BasePool"):
        for k, v in replacements.items():
            source = source.replace(k, v)

    return source
