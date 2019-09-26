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
    swap.functions.add_liquidity(0, 100 * U, int(time.time()) + 3600).\
        transact({'from': w3.eth.accounts[0]})

    # Adding the second time does a different calculation
    swap.functions.add_liquidity(0, 100 * U, int(time.time()) + 3600).\
        transact({'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because transaction is expired
        swap.functions.\
            add_liquidity(0, 100 * U, int(time.time()) - 3600).\
            transact({'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because this account has no coins
        swap.functions.\
            add_liquidity(0, 100 * U, int(time.time()) + 3600).\
            transact({'from': w3.eth.accounts[1]})

    # Reduce the allowance
    for c in coins:
        c.functions.approve(swap.address, 99 * U).\
            transact({'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because the allowance is now not enough
        swap.functions.\
            add_liquidity(0, 100 * U, int(time.time()) + 3600).\
            transact({'from': w3.eth.accounts[0]})

    for i in range(N_COINS):
        assert swap.caller.balances(0) == 200 * U


def test_ratio_preservation(w3, coins, swap, pool_token):
    alice, bob = w3.eth.accounts[:2]

    # Allow $1000 of each coin
    # Also give Bob something to trade with
    for c in coins:
        c.functions.approve(swap.address, 1000 * U).transact({'from': alice})
        c.functions.transfer(bob, 1000 * U).transact({'from': alice})
        c.functions.approve(swap.address, 1000 * U).transact({'from': bob})
    pool_token.functions.approve(swap.address, 1000 * U).transact({'from': alice})
    pool_token.functions.approve(swap.address, 1000 * U).transact({'from': bob})

    def assert_all_equal(address):
        balance_0 = coins[0].caller.balanceOf(address)
        swap_balance_0 = swap.caller.balances(0)
        for i in range(1, N_COINS):
            assert balance_0 == coins[i].caller.balanceOf(address)
            assert swap_balance_0 == swap.caller.balances(i)

    # Test that everything is equal when adding and removing liquidity
    for i in range(5):
        deadline = int(time.time()) + 3600
        value = random.randrange(100 * U)
        swap.functions.add_liquidity(0, value, deadline).transact({'from': alice})
        assert_all_equal(alice)
        value = random.randrange(100 * U)
        swap.functions.add_liquidity(0, value, deadline).transact({'from': bob})
        assert_all_equal(bob)
        value = random.randrange(10 * U)
        swap.functions.remove_liquidity(value, deadline).transact({'from': alice})
        assert_all_equal(alice)
        value = random.randrange(10 * U)
        swap.functions.remove_liquidity(value, deadline).transact({'from': bob})
        assert_all_equal(bob)
