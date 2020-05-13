import random
import pytest
from itertools import permutations
from eth_tester.exceptions import TransactionFailed
from .simulation import Curve
from .conftest import UU, PRECISIONS, use_lending

N_COINS = 3


def test_few_trades(w3, coins, cerc20s, swap, pool_token):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}
    bob = w3.eth.accounts[1]  # Bob the customer
    from_bob = {'from': bob}

    # Allow $1000 of each coin
    deposits = []
    for c, cc, u, l in zip(coins, cerc20s, UU, use_lending):
        if l:
            rate = cc.caller.exchangeRateStored() * (1 + len(deposits))
            cc.functions.set_exchange_rate(rate).transact(from_sam)
            c.functions.approve(cc.address, 1000 * u).transact(from_sam)
            cc.functions.mint(1000 * u).transact(from_sam)
            # Leave 90% of coins for trading - will trade compounded
            balance = cc.caller.balanceOf(sam)
        else:
            balance = 1000 * u
        deposits.append(balance)
        cc.functions.approve(swap.address, balance).transact(from_sam)

    # Adding $100 liquidity of each coin
    swap.functions.add_liquidity([b // 10 for b in deposits], 0).transact(from_sam)

    # Fund the customer with $100 of each coin
    for c, u in zip(cerc20s, UU):
        c.functions.transfer(bob, 100 * u).transact(from_sam)

    # Customer approves
    cerc20s[0].functions.approve(swap.address, 50 * UU[0]).transact(from_bob)

    # And trades
    with pytest.raises(TransactionFailed):
        # Cannot exchange to the same currency
        swap.functions.exchange(0, 0, 1 * UU[0], 0).transact(from_bob)

    swap.functions.exchange(
        0, 1, 1 * UU[0], int(0.9 * UU[1])
    ).transact(from_bob)

    assert cerc20s[0].caller.balanceOf(bob) == 99 * UU[0]
    assert cerc20s[1].caller.balanceOf(bob) > int(100.9 * UU[1])
    assert cerc20s[1].caller.balanceOf(bob) < 101 * UU[1]

    # Why not more
    swap.functions.exchange(
        0, 1, 1 * UU[0], int(0.9 * UU[1])
    ).transact(from_bob)

    assert cerc20s[0].caller.balanceOf(bob) == 98 * UU[0]
    assert cerc20s[1].caller.balanceOf(bob) > int(101.9 * UU[1])
    assert cerc20s[1].caller.balanceOf(bob) < 102 * UU[1]

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


def test_simulated_exchange(w3, coins, cerc20s, swap):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    bob = w3.eth.accounts[1]  # Bob the customer
    from_sam = {'from': sam}
    from_bob = {'from': bob}

    # Allow $1000 of each coin
    deposits = []
    for c, cc, u, l in zip(coins, cerc20s, UU, use_lending):
        if l:
            c.functions.approve(cc.address, 1000 * u).transact(from_sam)
            cc.functions.mint(1000 * u).transact(from_sam)
            balance = cc.caller.balanceOf(sam)
        else:
            balance = 1000 * u
        deposits.append(balance)
        cc.functions.approve(swap.address, balance).transact(from_sam)

    # Adding $100 liquidity of each coin
    liquidity = [b // 10 for b in deposits]
    swap.functions.add_liquidity(liquidity, 0).transact(from_sam)

    # Model
    balances = [int(swap.caller.balances(i)) for i in range(3)]
    rates = [int(c.caller.exchangeRateStored()) * p if l else 10 ** 18 * p
             for c, p, l in zip(cerc20s, PRECISIONS, use_lending)]
    curve = Curve(2 * 360, balances, N_COINS, rates)

    for c, u in zip(cerc20s, UU):
        # Fund the customer with $100 of each coin
        c.functions.transfer(bob, 100 * u).transact(from_sam)
        # Approve by Bob
        c.functions.approve(swap.address, 100 * u).transact(from_bob)

    # Start trading!
    for k in range(50):
        # Tune exchange rates
        for i, (cc, l) in enumerate(zip(cerc20s, use_lending)):
            if l:
                rate = int(cc.caller.exchangeRateCurrent() * 1.0001)
                cc.functions.set_exchange_rate(rate).transact(from_sam)
                curve.p[i] = rate * PRECISIONS[i]
        # In this particular case we have only one variable-rate coin
        # So we can reuse rate

        # Simulate the exchange
        old_virtual_price = swap.caller.get_virtual_price()
        i, j = random.choice(list(permutations(range(N_COINS), 2)))
        value = random.randrange(5 * UU[i])
        uvalue = value
        if i == 0:
            value = value * 10 ** 18 // rate  # price grew up, so less coins
        x_0 = cerc20s[i].caller.balanceOf(bob)
        y_0 = cerc20s[j].caller.balanceOf(bob)
        cerc20s[i].functions.approve(swap.address, 0).transact(from_bob)
        cerc20s[i].functions.approve(swap.address, value).transact(from_bob)
        swap.functions.exchange(
            i, j, value,
            int(0.5 * value * UU[j] / UU[i])  # rate is close to 1
        ).transact(from_bob)
        x_1 = cerc20s[i].caller.balanceOf(bob)
        y_1 = cerc20s[j].caller.balanceOf(bob)

        dy_m = curve.exchange(i, j, uvalue * max(UU) // UU[i]) * UU[j] // max(UU)
        if j == 0:
            dy_m = dy_m * rate // 10 ** 18

        assert x_0 - x_1 == value
        assert (y_1 - y_0) - dy_m < dy_m * 1e-10
        assert swap.caller.get_virtual_price() > old_virtual_price
        assert cerc20s[i].caller.balanceOf(swap.address) >= swap.caller.balances(i)
        assert cerc20s[j].caller.balanceOf(swap.address) >= swap.caller.balances(j)

    # Let's see what we have left
    x = [swap.caller.balances(i) for i in range(N_COINS)]
    assert tuple(round(a / b, 8) for a, b in zip(x, curve.x)) == (1.0,) * N_COINS

    assert sum(x[i] * rates[i] / 1e18 for i in range(N_COINS)) > 300 * max(UU)
