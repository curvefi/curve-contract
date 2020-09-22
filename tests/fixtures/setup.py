import pytest


@pytest.fixture(scope="module")
def add_initial_liquidity(alice, mint_alice, approve_alice, underlying_coins, swap, initial_amounts):
    # mint (10**7 * precision) of each coin in the pool
    eth_value = 0
    if "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" in underlying_coins:
        eth_value = 10 ** 24

    swap.add_liquidity(initial_amounts, 0, {'from': alice, 'value': eth_value})


@pytest.fixture(scope="module")
def mint_bob(bob, underlying_coins, wrapped_coins, initial_amounts):
    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        if underlying == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue

        if underlying != wrapped:
            underlying._mint_for_testing(bob, amount * 2, {'from': bob})
            underlying.approve(wrapped, 2**256-1, {'from': bob})
            wrapped.mint(amount, {'from': bob})
        else:
            underlying._mint_for_testing(bob, amount, {'from': bob})


@pytest.fixture(scope="module")
def approve_bob(bob, underlying_coins, wrapped_coins, swap, initial_amounts):
    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        if underlying == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue
        underlying.approve(swap, 2**256-1, {'from': bob})
        if underlying != wrapped:
            wrapped.approve(swap, 2**256-1, {'from': bob})


@pytest.fixture(scope="module")
def mint_alice(alice, underlying_coins, wrapped_coins, initial_amounts):
    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        if underlying == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue

        if underlying != wrapped:
            underlying._mint_for_testing(alice, amount * 2, {'from': alice})
            underlying.approve(wrapped, 2**256-1, {'from': alice})
            wrapped.mint(amount, {'from': alice})
        else:
            underlying._mint_for_testing(alice, amount, {'from': alice})


@pytest.fixture(scope="module")
def approve_alice(alice, underlying_coins, wrapped_coins, swap, initial_amounts):
    for underlying, wrapped, amount in zip(underlying_coins, wrapped_coins, initial_amounts):
        if underlying == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue
        underlying.approve(swap, 2**256-1, {'from': alice})
        if underlying != wrapped:
            wrapped.approve(swap, 2**256-1, {'from': alice})


@pytest.fixture(scope="module")
def approve_zap(alice, bob, zap, pool_token, underlying_coins, initial_amounts):
    for underlying, amount in zip(underlying_coins, initial_amounts):
        if underlying == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
            continue
        underlying.approve(zap, 2**256-1, {'from': alice})
        underlying.approve(zap, 2**256-1, {'from': bob})

    pool_token.approve(zap, 2**256-1, {'from': alice})
    pool_token.approve(zap, 2**256-1, {'from': bob})
