import pytest
import random
from itertools import permutations
from time import time
from eth_tester.exceptions import TransactionFailed
from .conftest import UU, use_lending, approx

N_COINS = 2


def test_transfer_ownership(tester, w3, swap):
    alice, bob, charlie = w3.eth.accounts[:3]

    # Only admin can withdraw fees
    # even if there are no fees, the call will fail for non-admin
    # Initially, the owner is Bob
    swap.functions.withdraw_admin_fees().transact({'from': bob})
    with pytest.raises(TransactionFailed):
        swap.functions.withdraw_admin_fees().transact({'from': alice})

    # Only allowed party can transfer ownership
    with pytest.raises(TransactionFailed):
        swap.functions.commit_transfer_ownership(alice).transact({'from': charlie})

    # Bob is allowed to do it
    swap.functions.commit_transfer_ownership(alice).transact({'from': bob})

    # However, Bob still cannot apply it
    with pytest.raises(TransactionFailed):
        swap.functions.apply_transfer_ownership().transact({'from': bob})

    # Travel a bit more than 7 days in future
    tester.time_travel(int(time()) + 86400 * 7 + 2000)
    tester.mine_block()

    # And now the ownership transfer should work
    swap.functions.apply_transfer_ownership().transact({'from': bob})

    # Test that transfer indeed occurred
    swap.functions.withdraw_admin_fees().transact({'from': alice})
    with pytest.raises(TransactionFailed):
        swap.functions.withdraw_admin_fees().transact({'from': bob})

    # Now test reverting it
    swap.functions.commit_transfer_ownership(charlie).transact({'from': alice})
    swap.functions.revert_transfer_ownership().transact({'from': alice})

    tester.time_travel(int(time()) + (86400 * 7 + 2000) * 2)
    tester.mine_block()

    # Cannot transfer after reverting
    with pytest.raises(TransactionFailed):
        swap.functions.apply_transfer_ownership().transact({'from': alice})


def test_trade_and_withdraw_fees(tester, w3, coins, yerc20s, swap):
    alice, owner, bob = w3.eth.accounts[:3]
    # Owner is the exchange admin
    # Alice and Bob trade

    # Owner wants to charge 20%
    swap.functions.commit_new_parameters(
        2 * 360, int(0.001 * 10 ** 10), int(0.2 * 10 ** 10)
        ).transact({'from': owner})

    deposits = []
    for c, cc, u, l in zip(coins, yerc20s, UU, use_lending):
        if l:
            c.functions.approve(cc.address, 2000 * u).transact({'from': alice})
            cc.functions.deposit(2000 * u).transact({'from': alice})
            balance = cc.caller.balanceOf(alice) // 2
        else:
            balance = 1000 * u
        deposits.append(balance)
        cc.functions.approve(swap.address, balance).transact({'from': alice})
        cc.functions.transfer(bob, balance).transact({'from': alice})
        cc.functions.approve(swap.address, balance).transact({'from': bob})

    swap.functions.add_liquidity(deposits, 0).transact({'from': alice})

    current_time = int(time()) + 86400 * 7 + 2000
    tester.time_travel(current_time)
    tester.mine_block()

    swap.functions.apply_new_parameters().transact({'from': owner})

    volumes = [0, 0, 0]

    for k in range(3):
        i, j = random.choice(list(permutations(range(N_COINS), 2)))
        value = int(random.random() * deposits[i] / 10)
        y_0 = yerc20s[j].caller.balanceOf(bob)
        yerc20s[i].functions.approve(swap.address, 0).transact({'from': bob})
        yerc20s[i].functions.approve(swap.address, value).transact({'from': bob})
        swap.functions.exchange(i, j, value, 0).transact({'from': bob})
        y_1 = yerc20s[j].caller.balanceOf(bob)

        volumes[j] += y_1 - y_0

    swap.functions.withdraw_admin_fees().transact({'from': owner})

    for v, c in zip(volumes, yerc20s):
        b = c.caller.balanceOf(owner)
        f = int((v / 0.999 - v) * 0.2)
        assert abs(f - b) <= 2 or approx(f, b, 1e-3)
