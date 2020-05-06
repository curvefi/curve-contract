import random
import pytest
from itertools import permutations
from eth_tester.exceptions import TransactionFailed
from .simulation import Curve
from .conftest import UU, PRECISIONS

N_COINS = 3


def test_few_trades(w3, coins, swap, pool_token):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}
    bob = w3.eth.accounts[1]  # Bob the customer
    from_bob = {'from': bob}

    # Allow $1000 of each coin
    deposits = []
    for c, u in zip(coins, UU):
        balance = 1000 * u
        deposits.append(balance)
        c.functions.approve(swap.address, balance).transact(from_sam)

    # Adding $100 liquidity of each coin
    swap.functions.add_liquidity([b // 10 for b in deposits], 0).transact(from_sam)

    # Fund the customer with $100 of each coin
    for c, u in zip(coins, UU):
        c.functions.transfer(bob, 100 * u).transact(from_sam)

    # Customer approves
    coins[0].functions.approve(swap.address, 50 * UU[0]).transact(from_bob)

    # And trades
    with pytest.raises(TransactionFailed):
        # Cannot exchange to the same currency
        swap.functions.exchange(0, 0, 1 * UU[0], 0).transact(from_bob)

    test_amount = deposits[0] // 10
    assert coins[0].caller.balanceOf(sam) > test_amount
    assert coins[0].caller.allowance(sam, swap.address) > test_amount
    with pytest.raises(TransactionFailed):
        # Cannot exchange to the same here, too
        swap.functions.exchange(0, 0, test_amount, 0).transact(from_sam)

    swap.functions.exchange(
        0, 1, 1 * UU[0], int(0.9 * UU[1])
    ).transact(from_bob)

    assert coins[0].caller.balanceOf(bob) == 99 * UU[0]
    assert coins[1].caller.balanceOf(bob) > int(100.9 * UU[1])
    assert coins[1].caller.balanceOf(bob) < 101 * UU[1]

    # Why not more
    swap.functions.exchange(
        0, 1, 1 * UU[0], int(0.9 * UU[1])
    ).transact(from_bob)

    assert coins[0].caller.balanceOf(bob) == 98 * UU[0]
    assert coins[1].caller.balanceOf(bob) > int(101.9 * UU[1])
    assert coins[1].caller.balanceOf(bob) < 102 * UU[1]

    # Oh no, a vulnerability detected! What do we do
    with pytest.raises(TransactionFailed):
        # No Sam, you're not an admin
        swap.functions.kill_me().transact(from_sam)
    # That account owns the contract
    swap.functions.kill_me().transact({'from': w3.eth.accounts[1]})

    # Cannot exchange now
    with pytest.raises(TransactionFailed):
        swap.functions.exchange(0, 1, 1 * UU[0], 0).transact(from_bob)

    # But can withdraw
    value = pool_token.caller.balanceOf(sam)
    swap.functions.remove_liquidity(value, [0] * N_COINS).transact(from_sam)


def test_simulated_exchange(w3, coins, swap):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    bob = w3.eth.accounts[1]  # Bob the customer
    from_sam = {'from': sam}
    from_bob = {'from': bob}

    # Allow $1000 of each coin
    deposits = []
    for c, u in zip(coins, UU):
        balance = 1000 * u
        deposits.append(balance)
        c.functions.approve(swap.address, balance).transact(from_sam)

    # Adding $100 liquidity of each coin
    liquidity = [b // 10 for b in deposits]
    swap.functions.add_liquidity(liquidity, 0).transact(from_sam)

    # Model
    balances = [int(swap.caller.balances(i)) for i in range(3)]
    curve = Curve(2 * 360, balances, N_COINS, [10 ** 18 * p for p in PRECISIONS])

    for c, u in zip(coins, UU):
        # Fund the customer with $100 of each coin
        c.functions.transfer(bob, 100 * u).transact(from_sam)
        # Approve by Bob
        c.functions.approve(swap.address, 100 * u).transact(from_bob)

    # Start trading!
    for k in range(50):
        # Simulate the exchange
        old_virtual_price = swap.caller.get_virtual_price()
        i, j = random.choice(list(permutations(range(N_COINS), 2)))
        value = random.randrange(5 * UU[i])
        x_0 = coins[i].caller.balanceOf(bob)
        y_0 = coins[j].caller.balanceOf(bob)
        coins[i].functions.approve(swap.address, 0).transact(from_bob)
        coins[i].functions.approve(swap.address, value).transact(from_bob)
        swap.functions.exchange(
            i, j, value,
            int(0.5 * value * UU[j] / UU[i])
        ).transact(from_bob)
        x_1 = coins[i].caller.balanceOf(bob)
        y_1 = coins[j].caller.balanceOf(bob)

        dy_m = curve.exchange(i, j, value * max(UU) // UU[i]) * UU[j] // max(UU)

        assert x_0 - x_1 == value
        assert (y_1 - y_0) - dy_m < dy_m * 1e-10
        assert swap.caller.get_virtual_price() > old_virtual_price
        assert coins[i].caller.balanceOf(swap.address) >= swap.caller.balances(i)
        assert coins[j].caller.balanceOf(swap.address) >= swap.caller.balances(j)

    # Let's see what we have left
    x = [swap.caller.balances(i) for i in range(N_COINS)]
    assert tuple(round(a / b, 10) for a, b in zip(x, curve.x)) == (1.0,) * N_COINS

    assert sum(x[i] * PRECISIONS[i] for i in range(N_COINS)) > 300 * max(UU)
