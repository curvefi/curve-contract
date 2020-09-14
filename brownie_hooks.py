"""
Compile-time hook used to set `StableSwap` constants.

In order to set the compile-time constants, set `DECIMALS` to the number
of decimal places for each underlying coin within the pool.
"""

# number of decimals for each underlying coin within the pool
DECIMALS = [18, 8]

# is each underlying coin lent out on the lending protocol associated with the given pool?
USE_LENDING = [True, True]


n_coins = len(DECIMALS)
precision_multiplier = [10**18 // (10**i) for i in DECIMALS]
rates = [i*10**18 for i in precision_multiplier]

replacements = {
    '___N_COINS___': str(n_coins),
    '___PRECISION_MUL___': str(precision_multiplier),
    '___RATES___': str(rates),
    '___USE_LENDING___': str(USE_LENDING),
}


def brownie_load_source(path, source):

    if len(DECIMALS) < 2:
        raise ValueError("Must set at least 2 decimal values in `brownie_hooks.py`")

    if path.stem.startswith("StableSwap") or path.stem.startswith("Deposit"):
        for k, v in replacements.items():
            source = source.replace(k, v)

    return source
