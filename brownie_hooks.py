"""
Compile-time hook used to set `StableSwap` constants.

This file should not be modified directly. Values are set based on the
`pooldata.json` file within each template subdirectory.
"""

import json


def brownie_load_source(path, source):

    if "pool-templates" not in path.parts:
        return source

    with path.parent.joinpath('pooldata.json').open() as fp:
        pool_data = json.load(fp)

    decimals = [i['decimals'] for i in pool_data['coins']]
    precision_multiplier = [10**18 // (10**i) for i in decimals]
    rates = [i*10**18 for i in precision_multiplier]

    replacements = {
        '___N_COINS___': len(decimals),
        '___PRECISION_MUL___': precision_multiplier,
        '___RATES___': rates,
        '___USE_LENDING___': [i['wrapped'] for i in pool_data['coins']],
    }

    for k, v in replacements.items():
        source = source.replace(k, str(v))

    return source
