import brownie


def test_incorrect_eth_amount(swap, bob, add_initial_liquidity, approve_bob):
    with brownie.reverts():
        swap.exchange(1, 0, 0, 0, {"from": bob, "value": "1 ether"})
