"""
Compile-time hook used to set `StableSwap` constants.

This file should not be modified directly. Values are set based on the
`pooldata.json` file within each template subdirectory.
"""

import json


def _load_pool_data(path):
    with path.parent.joinpath('pooldata.json').open() as fp:
        data = json.load(fp)

    decimals = [i['decimals'] for i in data['coins']]
    precision_multiplier = [10**18 // (10**i) for i in decimals]

    return {
        'n_coins': len(decimals),
        'decimals': decimals,
        'precision_mul': precision_multiplier,
        'rates': [i*10**18 for i in precision_multiplier],
        'lending': [i['wrapped'] for i in data['coins']],
        'base_pool_contract': data.get("base_pool_contract"),
    }


def brownie_load_source(path, source):

    if "pool-templates" not in path.parts:
        # compile-time substitution only applies to pool templates
        return source

    data_path = path.parent.joinpath('pooldata.json')
    pool_data = _load_pool_data(data_path)

    replacements = {
        '___N_COINS___': pool_data['n_coins'],
        '___PRECISION_MUL___': pool_data['precision_mul'],
        '___RATES___': pool_data['rates'],
        '___USE_LENDING___': pool_data['lending'],
    }

    if pool_data["base_pool_contract"]:
        # for metapools, also load pool data for the base pool
        contracts_dir = next(i for i in path.parents if i.name == "contracts")
        swap_dir = next(contracts_dir.glob(f"**/{pool_data['base_pool_contract']}.vy")).parent
        data_path = swap_dir.joinpath("pooldata.json")
        pool_data = _load_pool_data(data_path)
        replacements['___BASE_N_COINS___'] = pool_data['n_coins']

    for k, v in replacements.items():
        source = source.replace(k, str(v))

    return source
