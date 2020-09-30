import itertools
import pytest

pytestmark = pytest.mark.usefixtures("mint_alice", "approve_alice", "mint_bob", "approve_bob")


def test_swap_gas(
    chain,
    alice,
    bob,
    swap,
    n_coins,
    wrapped_decimals,
    underlying_decimals,
    initial_amounts,
):
    swap.add_liquidity(initial_amounts, 0, {'from': alice})
    chain.sleep(3600)

    for send, recv in itertools.permutations(range(n_coins), 2):
        amount = 10**wrapped_decimals[send]
        swap.exchange(send, recv, amount, 0, {'from': bob})
        chain.sleep(3600)

    if hasattr(swap, "exchange_underlying"):
        for send, recv in itertools.permutations(range(n_coins), 2):
            amount = 10**underlying_decimals[send]
            swap.exchange_underlying(send, recv, amount, 0, {'from': bob})
            chain.sleep(3600)

    swap.remove_liquidity(10**18, [0] * n_coins, {'from': alice})
    chain.sleep(3600)

    amounts = [10**wrapped_decimals[i] for i in range(n_coins)]
    swap.remove_liquidity_imbalance(amounts, 2**256-1, {'from': alice})
    chain.sleep(3600)

    if hasattr(swap, "remove_liquidity_one_coin"):
        for idx in range(n_coins):
            swap.remove_liquidity_one_coin(10**wrapped_decimals[idx], idx, 0, {'from': alice})
            chain.sleep(3600)


@pytest.mark.zap
def test_zap_gas(chain, alice, underlying_decimals, initial_amounts_underlying, zap, approve_zap):
    if not zap:
        return

    n_coins = len(initial_amounts_underlying)
    zap.add_liquidity(initial_amounts_underlying, 0, {'from': alice})
    chain.sleep(3600)

    zap.remove_liquidity(10**18, [0] * n_coins, {'from': alice})
    chain.sleep(3600)

    if hasattr(zap, "remove_liquidity_imbalance"):
        amounts = [10**underlying_decimals[i] for i in range(n_coins)]
        zap.remove_liquidity_imbalance(amounts, 2**256-1, {'from': alice})
        chain.sleep(3600)

    if hasattr(zap, "remove_liquidity_one_coin"):
        for idx in range(n_coins):
            zap.remove_liquidity_one_coin(10**underlying_decimals[idx], idx, 0, {'from': alice})
            chain.sleep(3600)
