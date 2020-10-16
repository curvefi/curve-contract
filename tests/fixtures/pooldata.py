import pytest


# pools

@pytest.fixture(scope="module")
def underlying_decimals(pool_data, base_pool_data):
    # number of decimal places for each underlying coin in the active pool
    if base_pool_data is None:
        return [i.get('decimals', i.get('wrapped_decimals')) for i in pool_data['coins']]
    return [pool_data['coins'][0]['decimals']] + [i['decimals'] for i in base_pool_data['coins']]


@pytest.fixture(scope="module")
def wrapped_decimals(pool_data):
    # number of decimal places for each wrapped coin in the active pool
    yield [i.get('wrapped_decimals', i.get('decimals')) for i in pool_data['coins']]


@pytest.fixture(scope="module")
def initial_amounts(wrapped_decimals):
    # 1e6 of each coin - used to make an even initial deposit in many test setups
    yield [10**(i+6) for i in wrapped_decimals]


@pytest.fixture(scope="module")
def initial_amounts_underlying(underlying_decimals, is_metapool, n_coins):
    amounts = [10**(i+6) for i in underlying_decimals]
    if is_metapool:
        # for a metapool, amount[0] == amount[1:] when wrapped
        divisor = len(underlying_decimals) - 1
        return [amounts[0]] + [i // divisor for i in amounts[1:]]
    else:
        return amounts


@pytest.fixture(scope="module")
def n_coins(pool_data):
    yield len(pool_data['coins'])


@pytest.fixture(scope="module")
def is_metapool(base_pool_data):
    return bool(base_pool_data)
