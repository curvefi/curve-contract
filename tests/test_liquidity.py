import time
import pytest
from eth_tester.exceptions import TransactionFailed

U = 10 ** 18


def test_add_liquidity(w3, coins, swap):
    # Allow $1000 of each coin
    for c in coins:
        c.approve(swap.address, 1000 * U,
                  transact={'from': w3.eth.accounts[0]})

    # Adding the first time
    swap.add_liquidity(0, 100 * U, 110 * U, int(time.time()) + 3600,
                       transact={'from': w3.eth.accounts[0]})

    # Adding the second time does a different calculation
    swap.add_liquidity(0, 100 * U, 110 * U, int(time.time()) + 3600,
                       transact={'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because we don't expect too much of other coins taken
        swap.add_liquidity(0, 100 * U, 99 * U, int(time.time()) + 3600,
                           transact={'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because transaction is expired
        swap.add_liquidity(0, 100 * U, 110 * U, int(time.time()) - 3600,
                           transact={'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because this account has no coins
        swap.add_liquidity(0, 100 * U, 110 * U, int(time.time()) + 3600,
                           transact={'from': w3.eth.accounts[1]})

    # Reduce the allowance
    for c in coins:
        c.approve(swap.address, 99 * U,
                  transact={'from': w3.eth.accounts[0]})

    with pytest.raises(TransactionFailed):
        # Fail because the allowance is now not enough
        swap.add_liquidity(0, 100 * U, 110 * U, int(time.time()) + 3600,
                           transact={'from': w3.eth.accounts[0]})
