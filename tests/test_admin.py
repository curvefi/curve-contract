import pytest
import random
from itertools import permutations
from time import time
from eth_tester.exceptions import TransactionFailed

U = 10 ** 18
N_COINS = 3


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


def test_trade_and_withdraw_fees(tester, w3, coins, swap):
    alice, owner, bob = w3.eth.accounts[:3]
    # Owner is the exchange admin
    # Alice and Bob trade

    # Owner wants to charge 20%
    swap.functions.commit_new_parameters(
        2 * 360, int(0.001 * 10 ** 10), int(0.2 * 10 ** 10)
        ).transact({'from': owner})

    for c in coins:
        c.functions.transfer(bob, 1000 * U).transact({'from': alice})
        c.functions.approve(swap.address, 1000 * U).transact({'from': alice})

    swap.functions.add_liquidity([1000 * U] * N_COINS, int(time()) + 3600).\
        transact({'from': alice})

    current_time = int(time()) + 86400 * 7 + 2000
    tester.time_travel(current_time)
    tester.mine_block()

    swap.functions.apply_new_parameters().transact({'from': owner})

    volumes = [0, 0, 0]

    for k in range(10):
        i, j = random.choice(list(permutations(range(N_COINS), 2)))
        value = random.randrange(100 * U)
        y_0 = coins[j].caller.balanceOf(bob)
        coins[i].functions.approve(swap.address, value).transact({'from': bob})
        swap.functions.exchange(i, j, value,
                                int(0.5 * value), current_time + 3600).\
            transact({'from': bob})
        y_1 = coins[j].caller.balanceOf(bob)

        volumes[j] += y_1 - y_0

    swap.functions.withdraw_admin_fees().transact({'from': owner})

    for v, c in zip(volumes, coins):
        b = c.caller.balanceOf(owner)
        f = int((v / 0.999 - v) * 0.2)
        assert abs(1 - b / f) < 2e-10 * 0.001
