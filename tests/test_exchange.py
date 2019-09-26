import time
import random
from itertools import permutations
from simulation import Curve

U = 10 ** 18
N_COINS = 3


def test_few_trades(w3, coins, swap):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    bob = w3.eth.accounts[1]  # Bob the customer

    # Allow $1000 of each coin
    for c in coins:
        c.functions.approve(swap.address, 1000 * U).transact({'from': sam})

    # Adding $100 liquidity of each coin
    swap.functions.add_liquidity(0, 100 * U, int(time.time()) + 3600).\
        transact({'from': sam})

    # Fund the customer with $100 of each coin
    for c in coins:
        c.functions.transfer(bob, 100 * U).transact({'from': sam})

    # Customer approves
    coins[0].functions.approve(swap.address, 50 * U).transact({'from': bob})

    # And trades
    swap.functions.exchange(0, 1, 1 * U,
                            int(0.9 * U), int(time.time()) + 3600).\
        transact({'from': bob})

    assert coins[0].caller.balanceOf(bob) == 99 * U
    assert coins[1].caller.balanceOf(bob) > int(100.9 * U)
    assert coins[1].caller.balanceOf(bob) < 101 * U

    # Why not more
    swap.functions.exchange(0, 1, 1 * U,
                            int(0.9 * U), int(time.time()) + 3600).\
        transact({'from': bob})

    assert coins[0].caller.balanceOf(bob) == 98 * U
    assert coins[1].caller.balanceOf(bob) > int(101.9 * U)
    assert coins[1].caller.balanceOf(bob) < 102 * U


def test_simulated_exchange(w3, coins, swap):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    bob = w3.eth.accounts[1]  # Bob the customer

    # Allow $1000 of each coin
    for c in coins:
        c.functions.approve(swap.address, 1000 * U).transact({'from': sam})

    # Adding $100 liquidity of each coin
    swap.functions.\
        add_liquidity(0, 100 * U, int(time.time()) + 3600).\
        transact({'from': sam})

    # Model
    curve = Curve(2 * 360, N_COINS * 100 * U, N_COINS)

    for c in coins:
        # Fund the customer with $100 of each coin
        c.functions.transfer(bob, 100 * U).transact({'from': sam})
        # Approve by Bob
        c.functions.approve(swap.address, 100 * U).transact({'from': bob})

    # Start trading!
    for k in range(50):
        i, j = random.choice(list(permutations(range(N_COINS), 2)))
        value = random.randrange(5 * U)
        x_0 = coins[i].caller.balanceOf(bob)
        y_0 = coins[j].caller.balanceOf(bob)
        swap.functions.exchange(i, j, value,
                                int(0.5 * value), int(time.time()) + 3600).\
            transact({'from': bob})
        x_1 = coins[i].caller.balanceOf(bob)
        y_1 = coins[j].caller.balanceOf(bob)

        dy_m = curve.exchange(i, j, value)

        assert x_0 - x_1 == value
        assert y_1 - y_0 == dy_m

    # Let's see what we have left
    x = [swap.caller.balances(i) for i in range(N_COINS)]
    assert tuple(x) == tuple(curve.x)

    assert sum(x) > 300 * U
