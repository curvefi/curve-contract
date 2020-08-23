
N_COINS = 2  # hBTC, wBTC
PRECISIONS = [8, 8]
USE_LENDING = [False, False]

replacements = {
    '___N_COINS___': str(N_COINS),
    '___PRECISION_MUL___': f"[{', '.join(str(10**18 // (10**i)) for i in PRECISIONS)}]",
    '___USE_LENDING___': f"[{', '.join(str(i) for i in USE_LENDING)}]"
}


def brownie_load_source(path, source):
    if path.stem in ("StableSwap",):
        for k, v in replacements.items():
            source = source.replace(k, v)

    return source
