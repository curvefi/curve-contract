import pytest


# shared logic for pool and base_pool setup fixtures

def _add_liquidity(acct, swap, coins, amounts):
    eth_value = 0
    if "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" in coins:
        eth_value = 10 ** 24

    swap.add_liquidity(amounts, 0, {'from': acct, 'value': eth_value})


def _mint(acct, wrapped_coins, wrapped_amounts, underlying_coins, underlying_amounts):
    for coin, amount in zip(wrapped_coins, wrapped_amounts):
        if coin == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue
        coin._mint_for_testing(acct, amount, {'from': acct})

    for coin, amount in zip(underlying_coins, underlying_amounts):
        if coin == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" or coin in wrapped_coins:
            continue
        coin._mint_for_testing(acct, amount, {'from': acct})


def _approve(owner, spender, *coins):
    for coin in set(x for i in coins for x in i):
        if coin == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue
        coin.approve(spender, 2**256-1, {'from': owner})


# pool setup fixtures

@pytest.fixture(scope="module")
def add_initial_liquidity(alice, mint_alice, approve_alice, underlying_coins, swap, initial_amounts):
    # mint (10**7 * precision) of each coin in the pool
    _add_liquidity(alice, swap, underlying_coins, initial_amounts)


@pytest.fixture(scope="module")
def mint_bob(bob, underlying_coins, wrapped_coins, initial_amounts, initial_amounts_underlying):
    _mint(bob, wrapped_coins, initial_amounts, underlying_coins, initial_amounts_underlying)


@pytest.fixture(scope="module")
def approve_bob(bob, swap, underlying_coins, wrapped_coins):
    _approve(bob, swap, underlying_coins, wrapped_coins)


@pytest.fixture(scope="module")
def mint_alice(alice, underlying_coins, wrapped_coins, initial_amounts, initial_amounts_underlying):
    _mint(alice, wrapped_coins, initial_amounts, underlying_coins, initial_amounts_underlying)


@pytest.fixture(scope="module")
def approve_alice(alice, swap, underlying_coins, wrapped_coins):
    _approve(alice, swap, underlying_coins, wrapped_coins)


@pytest.fixture(scope="module")
def approve_zap(alice, bob, zap, pool_token, underlying_coins, initial_amounts_underlying):
    for underlying, amount in zip(underlying_coins, initial_amounts_underlying):
        if underlying == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue
        underlying.approve(zap, 2**256-1, {'from': alice})
        underlying.approve(zap, 2**256-1, {'from': bob})

    pool_token.approve(zap, 2**256-1, {'from': alice})
    pool_token.approve(zap, 2**256-1, {'from': bob})


@pytest.fixture(scope="module")
def _add_base_pool_liquidity(charlie, base_swap, _base_coins, base_pool_data):
    # private fixture to add liquidity to the metapool
    if base_pool_data is None:
        return

    decimals = [i['decimals'] for i in base_pool_data['coins']]
    initial_amounts = [2 * 10**(i+6) for i in decimals]
    _mint(charlie, _base_coins, initial_amounts, [], [])
    _approve(charlie, base_swap, _base_coins)
    _add_liquidity(charlie, base_swap, _base_coins, initial_amounts)
