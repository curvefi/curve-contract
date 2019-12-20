import time
import pytest
import random
from eth_tester.exceptions import TransactionFailed
from .conftest import UU

N_COINS = 3


def test_add_liquidity(w3, coins, cerc20s, swap):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

    # Allow $1000 of each coin
    deposits = []
    for c, cc, u in zip(coins, cerc20s, UU):
        c.functions.approve(cc.address, 1000 * u).transact(from_sam)
        cc.functions.mint(1000 * u).transact(from_sam)
        balance = cc.caller.balanceOf(sam)
        deposits.append(balance)
        cc.functions.approve(swap.address, balance).transact(from_sam)

    # Adding the first time - $100 liquidity of each coin
    swap.functions.add_liquidity(
        [b // 10 for b in deposits], int(time.time()) + 3600
    ).transact(from_sam)

    # Adding the second time does a different calculation
    swap.functions.add_liquidity(
        [b // 10 for b in deposits], int(time.time()) + 3600
    ).transact(from_sam)

    with pytest.raises(TransactionFailed):
        # Fail because transaction is expired
        swap.functions.add_liquidity(
            [b // 10 for b in deposits], int(time.time()) - 3600
        ).transact(from_sam)

    with pytest.raises(TransactionFailed):
        # Fail because this account has no coins
        swap.functions.add_liquidity(
            [b // 10 for b in deposits], int(time.time()) + 3600
        ).transact({'from': w3.eth.accounts[1]})

    # Reduce the allowance
    for cc, b in zip(cerc20s, deposits):
        cc.functions.approve(swap.address, int(b * 0.099)).transact(from_sam)

    with pytest.raises(TransactionFailed):
        # Fail because the allowance is now not enough
        swap.functions.add_liquidity(
            [b // 10 for b in deposits], int(time.time()) + 3600
        ).transact(from_sam)

    for i, b in enumerate(deposits):
        assert swap.caller.balances(i) == b // 5


# @pytest.mark.parametrize('iteration', range(40))
def test_ratio_preservation(w3, coins, swap, pool_token):
    alice, bob = w3.eth.accounts[:2]
    dust = 5

    # Allow $1000 of each coin
    # Also give Bob something to trade with
    alice_balances = []
    bob_balances = []
    for c, u in zip(coins, UU):
        c.functions.approve(swap.address, 1000 * u).transact({'from': alice})
        c.functions.transfer(bob, 1000 * u).transact({'from': alice})
        c.functions.approve(swap.address, 1000 * u).transact({'from': bob})
        alice_balances.append(c.caller.balanceOf(alice))
        bob_balances.append(c.caller.balanceOf(bob))
    pool_token.functions.approve(swap.address, 10000 * max(UU)).transact({'from': alice})
    pool_token.functions.approve(swap.address, 10000 * max(UU)).transact({'from': bob})

    def assert_all_equal(address):
        balance_0 = coins[0].caller.balanceOf(address) * max(UU) // UU[0]
        swap_balance_0 = swap.caller.balances(0)
        for i in range(1, N_COINS):
            assert abs(balance_0 * UU[i] // max(UU) - coins[i].caller.balanceOf(address)) <= 5
            assert swap_balance_0 == swap.caller.balances(i)

    # Test that everything is equal when adding and removing liquidity
    deadline = int(time.time()) + 3600
    swap.functions.add_liquidity([50 * u for u in UU], deadline).transact({'from': alice})
    swap.functions.add_liquidity([50 * u for u in UU], deadline).transact({'from': bob})
    for i in range(5):
        value = random.randrange(1, 100)
        swap.functions.add_liquidity([value * u for u in UU], deadline).transact({'from': alice})
        assert_all_equal(alice)
        value = random.randrange(1, 100)
        swap.functions.add_liquidity([value * u for u in UU], deadline).transact({'from': bob})
        assert_all_equal(bob)
        value = random.randrange(10 * max(UU))
        swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
            transact({'from': alice})
        assert_all_equal(alice)
        value = random.randrange(10 * max(UU))
        swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
            transact({'from': bob})
        assert_all_equal(bob)

    # And let's withdraw all
    value = pool_token.caller.balanceOf(alice)
    with pytest.raises(TransactionFailed):
        # Cannot withdraw more than the limits we've set
        swap.functions.remove_liquidity(value, deadline, [value + 1] * N_COINS).\
            transact({'from': alice})
    swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
        transact({'from': alice})
    value = pool_token.caller.balanceOf(bob)
    swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
        transact({'from': bob})

    for i in range(N_COINS):
        assert abs(coins[i].caller.balanceOf(alice) - alice_balances[i]) <= dust
        assert abs(coins[i].caller.balanceOf(bob) - bob_balances[i]) <= dust
        assert swap.caller.balances(i) == 0
    assert pool_token.caller.totalSupply() == 0


def test_remove_liquidity_imbalance(w3, coins, swap, pool_token):
    alice, bob, charlie = w3.eth.accounts[:3]
    deadline = int(time.time()) + 3600

    # Allow $1000 of each coin
    # Also give Bob something to trade with
    alice_balances = []
    bob_balances = []
    for c, u in zip(coins, UU):
        c.functions.approve(swap.address, 1000 * u).transact({'from': alice})
        c.functions.transfer(bob, 1000 * u).transact({'from': alice})
        c.functions.approve(swap.address, 1000 * u).transact({'from': bob})
        alice_balances.append(c.caller.balanceOf(alice))
        bob_balances.append(c.caller.balanceOf(bob))
    pool_token.functions.approve(swap.address, 20000 * max(UU)).transact({'from': alice})
    pool_token.functions.approve(swap.address, 20000 * max(UU)).transact({'from': bob})

    # First, both fund the thing in equal amount
    swap.functions.add_liquidity([1000 * u for u in UU], deadline).\
        transact({'from': alice})
    swap.functions.add_liquidity([1000 * u for u in UU], deadline).\
        transact({'from': bob})

    bob_volumes = [0] * N_COINS
    for i in range(10):
        # Now Bob withdraws and adds coins in the same proportion, losing his
        # fees to Alice
        values = [random.randrange(900 * u / N_COINS) for u in UU]
        for i in range(N_COINS):
            bob_volumes[i] += values[i]
        swap.functions.remove_liquidity_imbalance(values, deadline).\
            transact({'from': bob})
        for c, u in zip(coins, UU):
            c.functions.approve(swap.address, 1000 * u).transact({'from': bob})
        swap.functions.add_liquidity(values, deadline).transact({'from': bob})

    # After this, coins should be in equal proportion, but Alice should have
    # more
    value = pool_token.caller.balanceOf(alice)
    swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
        transact({'from': alice})
    value = pool_token.caller.balanceOf(bob)
    swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
        transact({'from': bob})

    for i in range(N_COINS):
        alice_grow = coins[i].caller.balanceOf(alice) - alice_balances[i]
        bob_grow = coins[i].caller.balanceOf(bob) - bob_balances[i]
        assert swap.caller.balances(i) == 0
        assert alice_grow > 0
        assert bob_grow < 0
        assert abs(alice_grow + bob_grow) < 5
        grow_fee_ratio = alice_grow / int(bob_volumes[i] * 0.001)
        # Part of the fees are earned by Bob: he also had liquidity
        assert grow_fee_ratio > 0 and grow_fee_ratio <= 1

    # Now Alice adds liquiduty and Bob tries to "trade" by adding and removing
    # liquidity. Should be equivalent of exchange
    v_before = sum(c.caller.balanceOf(alice) * max(UU) // u for c, u in zip(coins, UU))
    for c, u in zip(coins, UU):
        c.functions.approve(swap.address, 1000 * u).transact({'from': alice})
        c.functions.approve(swap.address, 1000 * u).transact({'from': bob})
    swap.functions.add_liquidity([100 * u for u in UU], deadline).\
        transact({'from': alice})
    swap.functions.add_liquidity([UU[0], 0, 0], deadline).\
        transact({'from': bob})
    with pytest.raises(TransactionFailed):
        # Cannot remove all because of fees
        swap.functions.remove_liquidity_imbalance([0, UU[1], 0], deadline).\
            transact({'from': bob})
    swap.functions.remove_liquidity_imbalance([0, int(0.995 * UU[1]), 0], deadline).\
        transact({'from': bob})
    # Let's see how much Alice got now
    value = pool_token.caller.balanceOf(alice)
    swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
        transact({'from': alice})
    v_after = sum(c.caller.balanceOf(alice) * max(UU) // u for c, u in zip(coins, UU))
    assert abs((v_after - v_before) / (0.995 * max(UU) * 0.001) - 1) < 0.05
