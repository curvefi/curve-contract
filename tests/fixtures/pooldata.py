import pytest

# pools


@pytest.fixture(scope="module")
def underlying_decimals(pool_data, base_pool_data):
    # number of decimal places for each underlying coin in the active pool
    decimals = [i.get("decimals", i.get("wrapped_decimals")) for i in pool_data["coins"]]

    if base_pool_data is None:
        return decimals
    base_decimals = [i.get("decimals", i.get("wrapped_decimals")) for i in base_pool_data["coins"]]
    return decimals[:-1] + base_decimals


@pytest.fixture(scope="module")
def wrapped_decimals(pool_data):
    # number of decimal places for each wrapped coin in the active pool
    yield [i.get("wrapped_decimals", i.get("decimals")) for i in pool_data["coins"]]


@pytest.fixture(scope="module")
def base_amount(base_pool_data, pool_data):
    try:
        amount = pool_data["testing"]["initial_amount"]
    except KeyError:
        amount = 1000000
    try:
        amount = min(amount, base_pool_data["testing"]["initial_amount"])
    except (KeyError, TypeError):
        pass
    yield amount


@pytest.fixture(scope="module")
def initial_amounts(wrapped_decimals, base_amount):
    # 1e6 of each coin - used to make an even initial deposit in many test setups
    yield [10 ** i * base_amount for i in wrapped_decimals]


@pytest.fixture(scope="module")
def initial_amounts_underlying(underlying_decimals, base_amount, is_metapool, n_coins):
    amounts = [10 ** i * base_amount for i in underlying_decimals]
    if is_metapool:
        # for a metapool, amount[0] == amount[1:] when wrapped
        divisor = len(underlying_decimals) - 1
        return [amounts[0]] + [i // divisor for i in amounts[1:]]
    else:
        return amounts


@pytest.fixture(scope="module")
def n_coins(pool_data):
    yield len(pool_data["coins"])


@pytest.fixture(scope="module")
def is_metapool(pool_data):
    return "meta" in pool_data.get("pool_types", [])
