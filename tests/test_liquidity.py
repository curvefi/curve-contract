import pytest
import random
from eth_tester.exceptions import TransactionFailed
from .conftest import UU, use_lending

N_COINS = 3


def test_add_liquidity(w3, coins, cerc20s, swap):
    sam = w3.eth.accounts[0]  # Sam owns the bank
    from_sam = {'from': sam}

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

    # Adding the first time - $100 liquidity of each coin
    swap.functions.add_liquidity([b // 10 for b in deposits]).transact(from_sam)

    # Adding the second time does a different calculation
    swap.functions.add_liquidity([b // 10 for b in deposits]).transact(from_sam)

    with pytest.raises(TransactionFailed):
        # Fail because this account has no coins
        swap.functions.add_liquidity(
            [b // 10 for b in deposits]
        ).transact({'from': w3.eth.accounts[1]})

    # Reduce the allowance
    for cc, b in zip(cerc20s, deposits):
        cc.functions.approve(swap.address, 0).transact(from_sam)
        cc.functions.approve(swap.address, int(b * 0.099)).transact(from_sam)

    with pytest.raises(TransactionFailed):
        # Fail because the allowance is now not enough
        swap.functions.add_liquidity(
            [b // 10 for b in deposits]
        ).transact(from_sam)

    for i, b in enumerate(deposits):
        assert swap.caller.balances(i) == b // 5


# @pytest.mark.parametrize('iteration', range(40))
def test_ratio_preservation(w3, coins, cerc20s, swap, pool_token):
    alice, bob = w3.eth.accounts[:2]
    mtgox = w3.eth.accounts[2]  # <- all unneeded coins are dumped here
    dust = 1e-8

    # Allow $1000 of each coin
    # Also give Bob something to trade with
    alice_balances = []
    bob_balances = []
    deposits = []
    for c, cc, u, l in zip(coins, cerc20s, UU, use_lending):
        if l:
            c.functions.approve(cc.address, 2000 * u).transact({'from': alice})
            cc.functions.mint(2000 * u).transact({'from': alice})
            balance = cc.caller.balanceOf(alice) // 2
        else:
            balance = 1000 * u
            big_balance = cc.caller.balanceOf(alice)
            cc.functions.transfer(mtgox, big_balance - 2 * balance).transact({'from': alice})
        deposits.append(balance)
        cc.functions.approve(swap.address, balance).transact({'from': alice})
        cc.functions.transfer(bob, balance).transact({'from': alice})
        cc.functions.approve(swap.address, balance).transact({'from': bob})
        alice_balances.append(cc.caller.balanceOf(alice))
        bob_balances.append(cc.caller.balanceOf(bob))

    rates = [cc.caller.exchangeRateStored() if l else 10 ** 18
             for cc, l in zip(cerc20s, use_lending)]

    def assert_all_equal(address):
        balance_0 = cerc20s[0].caller.balanceOf(address) * rates[0] // UU[0]
        swap_balance_0 = swap.caller.balances(0) * rates[0] // UU[0]
        for i in range(1, N_COINS):
            balance_i = cerc20s[i].caller.balanceOf(address) * rates[i] // UU[i]
            swap_balance_i = swap.caller.balances(i) * rates[i] // UU[i]
            assert abs(balance_0 - balance_i) / (balance_0 + balance_i) < dust
            assert abs(swap_balance_0 - swap_balance_i) / (swap_balance_0 + swap_balance_i) < dust
            assert cerc20s[i].caller.balanceOf(swap.address) >= swap.caller.balances(i)

    # Test that everything is equal when adding and removing liquidity
    swap.functions.add_liquidity([d // 20 for d in deposits]).transact({'from': alice})
    swap.functions.add_liquidity([d // 20 for d in deposits]).transact({'from': bob})
    k_pool = [(deposits[i] // 20) / pool_token.caller.balanceOf(alice)
              for i in range(N_COINS)]
    old_virtual_price = swap.caller.get_virtual_price()
    for i in range(5):
        # Add liquidity from Alice
        value = random.randrange(1, 100)  # for 1e6 coins, error is ~1e-8
        swap.functions.add_liquidity(
            [value * d // 1000 for d in deposits]
        ).transact({'from': alice})
        assert_all_equal(alice)
        diff = (swap.caller.get_virtual_price() / old_virtual_price) - 1
        assert diff >= 0 and diff < dust
        # Add liquidity from Bob
        value = random.randrange(1, 100)
        swap.functions.add_liquidity(
            [value * d // 1000 for d in deposits]
        ).transact({'from': bob})
        assert_all_equal(bob)
        diff = (swap.caller.get_virtual_price() / old_virtual_price) - 1
        assert diff >= 0 and diff < dust
        # Remove liquidity from Alice
        value = random.randrange(10 * max(UU))
        swap.functions.remove_liquidity(value, [0] * N_COINS).\
            transact({'from': alice})
        assert_all_equal(alice)
        diff = (swap.caller.get_virtual_price() / old_virtual_price) - 1
        assert diff >= 0 and diff < dust
        # Remove liquidity from Bob
        value = random.randrange(10 * max(UU))
        swap.functions.remove_liquidity(value, [0] * N_COINS).\
            transact({'from': bob})
        assert_all_equal(bob)
        diff = (swap.caller.get_virtual_price() / old_virtual_price) - 1
        assert diff >= 0 and diff < dust

    # And let's withdraw all
    value = pool_token.caller.balanceOf(alice)
    with pytest.raises(TransactionFailed):
        # Cannot withdraw less than the limits we've set
        swap.functions.remove_liquidity(
            value, [int(value * k * 1.0001) for k in k_pool]
        ).transact({'from': alice})
    swap.functions.remove_liquidity(value, [0] * N_COINS).\
        transact({'from': alice})
    value = pool_token.caller.balanceOf(bob)
    swap.functions.remove_liquidity(value, [0] * N_COINS).\
        transact({'from': bob})

    for i in range(N_COINS):
        assert abs(cerc20s[i].caller.balanceOf(alice) / alice_balances[i] - 1) <= dust
        assert abs(cerc20s[i].caller.balanceOf(bob) / bob_balances[i] - 1) <= dust
        assert swap.caller.balances(i) == 0
    assert pool_token.caller.totalSupply() == 0


def test_remove_liquidity_imbalance(w3, coins, cerc20s, swap, pool_token):
    alice, bob, charlie = w3.eth.accounts[:3]
    mtgox = w3.eth.accounts[3]  # <- all unneeded coins are dumped here

    # Allow $1000 of each coin
    # Also give Bob something to trade with
    alice_balances = []
    bob_balances = []
    deposits = []
    for c, cc, u, l in zip(coins, cerc20s, UU, use_lending):
        if l:
            c.functions.approve(cc.address, 2000 * u).transact({'from': alice})
            cc.functions.mint(2000 * u).transact({'from': alice})
            balance = cc.caller.balanceOf(alice) // 2
        else:
            balance = 1000 * u
            big_balance = cc.caller.balanceOf(alice)
            cc.functions.transfer(mtgox, big_balance - 2 * balance).transact({'from': alice})
        deposits.append(balance)
        cc.functions.approve(swap.address, balance).transact({'from': alice})
        cc.functions.transfer(bob, balance).transact({'from': alice})
        cc.functions.approve(swap.address, balance).transact({'from': bob})
        alice_balances.append(cc.caller.balanceOf(alice))
        bob_balances.append(cc.caller.balanceOf(bob))

    rates = [cc.caller.exchangeRateStored() if l else 10 ** 18
             for cc, l in zip(cerc20s, use_lending)]

    # First, both fund the thing in equal amount
    swap.functions.add_liquidity(deposits).transact({'from': alice})
    swap.functions.add_liquidity(deposits).transact({'from': bob})

    bob_volumes = [0] * N_COINS
    for i in range(10):
        # Now Bob withdraws and adds coins in the same proportion, losing his
        # fees to Alice
        values = [max(int(b * random.random() * 0.3), 1000) for b in deposits]
        for i in range(N_COINS):
            bob_volumes[i] += values[i]
        swap.functions.remove_liquidity_imbalance(values).\
            transact({'from': bob})
        for cc, v in zip(cerc20s, values):
            cc.functions.approve(swap.address, v).transact({'from': bob})
        swap.functions.add_liquidity(values).transact({'from': bob})

    # After this, coins should be in equal proportion, but Alice should have
    # more
    value = pool_token.caller.balanceOf(alice)
    swap.functions.remove_liquidity(value, [0] * N_COINS).\
        transact({'from': alice})
    value = pool_token.caller.balanceOf(bob)
    swap.functions.remove_liquidity(value, [0] * N_COINS).\
        transact({'from': bob})

    for i in range(N_COINS):
        alice_grow = cerc20s[i].caller.balanceOf(alice) - alice_balances[i]
        bob_grow = cerc20s[i].caller.balanceOf(bob) - bob_balances[i]
        assert swap.caller.balances(i) == 0
        assert alice_grow > 0
        assert bob_grow < 0
        assert abs(alice_grow + bob_grow) < 5
        grow_fee_ratio = alice_grow / int(bob_volumes[i] * 0.001)
        # Part of the fees are earned by Bob: he also had liquidity
        assert grow_fee_ratio > 0 and grow_fee_ratio <= 1

    # Now Alice adds liquiduty and Bob tries to "trade" by adding and removing
    # liquidity. Should be equivalent of exchange
    v_before = sum(c.caller.balanceOf(alice) * r // u for c, r, u in zip(cerc20s, rates, UU))
    for cc, b in zip(cerc20s, deposits):
        cc.functions.approve(swap.address, b).transact({'from': alice})
        cc.functions.approve(swap.address, b).transact({'from': bob})
    swap.functions.add_liquidity([b // 10 for b in deposits]).\
        transact({'from': alice})
    swap.functions.add_liquidity([deposits[0] // 1000, 0, 0]).\
        transact({'from': bob})
    with pytest.raises(TransactionFailed):
        # Cannot remove all because of fees
        swap.functions.remove_liquidity_imbalance(
            [0, deposits[1] // 1000, 0]
        ).transact({'from': bob})
    swap.functions.remove_liquidity_imbalance(
        [0, int(0.995 * deposits[1] / 1000), 0]
    ).transact({'from': bob})
    # Let's see how much Alice got now
    value = pool_token.caller.balanceOf(alice)
    swap.functions.remove_liquidity(value, [0] * N_COINS).\
        transact({'from': alice})
    v_after = sum(c.caller.balanceOf(alice) * r // u for c, r, u in zip(cerc20s, rates, UU))
    assert abs((v_after - v_before) / (max(UU) * 0.001) - 1) < 0.05
    for i in range(N_COINS):
        assert cerc20s[i].caller.balanceOf(swap.address) >= swap.caller.balances(i)
