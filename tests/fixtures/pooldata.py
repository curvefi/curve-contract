import pytest


# pool-dependent data fixtures

@pytest.fixture(scope="module")
def underlying_decimals(pool_data):
    # number of decimal places for each underlying coin in the active pool
    yield [i['decimals'] for i in pool_data['coins']]


@pytest.fixture(scope="module")
def wrapped_decimals(pool_data):
    # number of decimal places for each wrapped coin in the active pool
    yield [i.get('wrapped_decimals', i['decimals']) for i in pool_data['coins']]


@pytest.fixture(scope="module")
def initial_amounts(wrapped_decimals):
    # 1e6 of each coin - used to make an even initial deposit in many test setups
    yield [10**(i+6) for i in wrapped_decimals]


@pytest.fixture(scope="module")
def n_coins(pool_data):
    yield len(pool_data['coins'])
