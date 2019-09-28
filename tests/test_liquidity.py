import time
import pytest
import random
from eth_tester.exceptions import TransactionFailed

U = 10 ** 18
N_COINS = 3


def test_add_liquidity(w3, coins, swap):
    # Allow $1000 of each coin
    for c in coins:
        c.functions.approve(swap.address, 1000 * U).\
            transact({'from': w3.eth.accounts[0]})

    # Adding the first time
    swap.functions.add_liquidity([100 * U] * N_COINS, int(time.time()) + 3600).\
        transact({'from': w3.eth.accounts[0]})

    # Adding the second time does a different calculation
    swap.functions.add_liquidity([100 * U] * N_COINS, int(time.time()) + 3600).\
        transact({'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because transaction is expired
        swap.functions.\
            add_liquidity([100 * U] * N_COINS, int(time.time()) - 3600).\
            transact({'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because this account has no coins
        swap.functions.\
            add_liquidity([100 * U] * N_COINS, int(time.time()) + 3600).\
            transact({'from': w3.eth.accounts[1]})

    # Reduce the allowance
    for c in coins:
        c.functions.approve(swap.address, 99 * U).\
            transact({'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because the allowance is now not enough
        swap.functions.\
            add_liquidity([100 * U] * N_COINS, int(time.time()) + 3600).\
            transact({'from': w3.eth.accounts[0]})

    for i in range(N_COINS):
        assert swap.caller.balances(0) == 200 * U


# @pytest.mark.parametrize('iteration', range(40))
def test_ratio_preservation(w3, coins, swap, pool_token):
    alice, bob = w3.eth.accounts[:2]
    dust = 5

    # Allow $1000 of each coin
    # Also give Bob something to trade with
    alice_balances = []
    bob_balances = []
    for c in coins:
        c.functions.approve(swap.address, 1000 * U).transact({'from': alice})
        c.functions.transfer(bob, 1000 * U).transact({'from': alice})
        c.functions.approve(swap.address, 1000 * U).transact({'from': bob})
        alice_balances.append(c.caller.balanceOf(alice))
        bob_balances.append(c.caller.balanceOf(bob))
    pool_token.functions.approve(swap.address, 10000 * U).transact({'from': alice})
    pool_token.functions.approve(swap.address, 10000 * U).transact({'from': bob})

    def assert_all_equal(address):
        balance_0 = coins[0].caller.balanceOf(address)
        swap_balance_0 = swap.caller.balances(0)
        for i in range(1, N_COINS):
            assert balance_0 == coins[i].caller.balanceOf(address)
            assert swap_balance_0 == swap.caller.balances(i)

    # Test that everything is equal when adding and removing liquidity
    deadline = int(time.time()) + 3600
    swap.functions.add_liquidity([50 * U] * N_COINS, deadline).transact({'from': alice})
    swap.functions.add_liquidity([50 * U] * N_COINS, deadline).transact({'from': bob})
    for i in range(5):
        value = random.randrange(100 * U)
        swap.functions.add_liquidity([value] * N_COINS, deadline).transact({'from': alice})
        assert_all_equal(alice)
        value = random.randrange(100 * U)
        swap.functions.add_liquidity([value] * N_COINS, deadline).transact({'from': bob})
        assert_all_equal(bob)
        value = random.randrange(10 * U)
        swap.functions.remove_liquidity(value, deadline, [0] * N_COINS).\
            transact({'from': alice})
        assert_all_equal(alice)
        value = random.randrange(10 * U)
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
    for c in coins:
        c.functions.approve(swap.address, 1000 * U).transact({'from': alice})
        c.functions.transfer(bob, 1000 * U).transact({'from': alice})
        c.functions.approve(swap.address, 1000 * U).transact({'from': bob})
        alice_balances.append(c.caller.balanceOf(alice))
        bob_balances.append(c.caller.balanceOf(bob))
    pool_token.functions.approve(swap.address, 20000 * U).transact({'from': alice})
    pool_token.functions.approve(swap.address, 20000 * U).transact({'from': bob})

    # First, both fund the thing in equal amount
    swap.functions.add_liquidity([1000 * U] * N_COINS, deadline).\
        transact({'from': alice})
    swap.functions.add_liquidity([1000 * U] * N_COINS, deadline).\
        transact({'from': bob})

    bob_volumes = [0] * N_COINS
    for i in range(10):
        # Now Bob withdraws and adds coins in the same proportion, losing his
        # fees to Alice
        values = [random.randrange(900 * U / N_COINS) for i in range(N_COINS)]
        for i in range(N_COINS):
            bob_volumes[i] += values[i]
        swap.functions.remove_liquidity_imbalance(values, deadline).\
            transact({'from': bob})
        for c in coins:
            c.functions.approve(swap.address, 1000 * U).transact({'from': bob})
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
        assert alice_grow + bob_grow == 0
        grow_fee_ratio = alice_grow / int(bob_volumes[i] * 0.001)
        # Part of the fees are earned by Bob: he also had liquidity
        assert grow_fee_ratio > 0 and grow_fee_ratio <= 1
