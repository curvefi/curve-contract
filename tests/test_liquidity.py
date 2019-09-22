import time


def test_add_liquidity(w3, coins, swap):
    # Allow $1000 of each coin
    for c in coins:
        c.approve(swap.address, 1000 * 10 ** 18,
                  transact={'from': w3.eth.accounts[0]})

    swap.add_liquidity(0, 100, 110, int(time.time()) + 3600,
                       transact={'from': w3.eth.accounts[0]})
