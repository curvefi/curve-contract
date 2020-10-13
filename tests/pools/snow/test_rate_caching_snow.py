import pytest


pytestmark = pytest.mark.usefixtures("add_initial_liquidity", "mint_bob", "approve_bob")


def test_initial_assumptions(alice, swap):
    assert swap.get_coin_rates() == [10**18] * 6


def test_get_coin_rates_caching(chain, alice, swap, wrapped_coins):
    rates = [10**18 * (1 + i/100) for i in range(1, 6)] + [10**18]
    for rate, coin in zip(rates, wrapped_coins[:-1]):
        coin.set_exchange_rate(rate)

    # modified rates should not take effect immediately
    assert swap.get_coin_rates() == [10**18] * 6

    chain.sleep(601)
    chain.mine()

    # 10 minutes later, they should be visible
    assert swap.get_coin_rates() == rates


def test_add_liquidity(chain, bob, swap, wrapped_coins, wrapped_decimals):
    amounts = [10**i for i in wrapped_decimals]

    rates = [10**18 * (1 + i/100) for i in range(1, 6)] + [10**18]
    for rate, coin in zip(rates, wrapped_coins[:-1]):
        coin.set_exchange_rate(rate)

    swap.add_liquidity(amounts, 0, {'from': bob})
    assert swap.get_coin_rates() == [10**18] * 6

    chain.sleep(601)

    swap.add_liquidity(amounts, 0, {'from': bob})
    assert swap.get_coin_rates() == rates


def test_exchange(chain, bob, swap, wrapped_coins, wrapped_decimals):
    rates = [10**18 * (1 + i/100) for i in range(1, 6)] + [10**18]
    for rate, coin in zip(rates, wrapped_coins[:-1]):
        coin.set_exchange_rate(rate)

    swap.exchange(0, 1, 10**18, 0, {'from': bob})
    assert swap.get_coin_rates() == [10**18] * 6

    chain.sleep(601)

    swap.exchange(0, 1, 10**18, 0, {'from': bob})
    assert swap.get_coin_rates() == rates


def test_remove_liquidity_imbalance(chain, alice, swap, wrapped_coins, wrapped_decimals):
    amounts = [10**i for i in wrapped_decimals]

    rates = [10**18 * (1 + i/100) for i in range(1, 6)] + [10**18]
    for rate, coin in zip(rates, wrapped_coins[:-1]):
        coin.set_exchange_rate(rate)

    swap.remove_liquidity_imbalance(amounts, 2**256-1, {'from': alice})
    assert swap.get_coin_rates() == [10**18] * 6

    chain.sleep(601)

    swap.remove_liquidity_imbalance(amounts, 2**256-1, {'from': alice})
    assert swap.get_coin_rates() == rates


def test_remove_liquidity_one_coin(chain, alice, swap, wrapped_coins):
    rates = [10**18 * (1 + i/100) for i in range(1, 6)] + [10**18]
    for rate, coin in zip(rates, wrapped_coins[:-1]):
        coin.set_exchange_rate(rate)

    swap.remove_liquidity_one_coin(10**18, 0, 0, {'from': alice})
    assert swap.get_coin_rates() == [10**18] * 6

    chain.sleep(601)

    swap.remove_liquidity_one_coin(10**18, 0, 0, {'from': alice})
    assert swap.get_coin_rates() == rates
