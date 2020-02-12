def test_yerc20(w3, coins, yerc20s):
    from_creator = {'from': w3.eth.accounts[0]}
    bob = w3.eth.accounts[1]
    from_bob = {'from': bob}
    for t, y in zip(coins, yerc20s):
        amount = 10 ** 5 * 10 ** t.caller.decimals()
        t.functions.transfer(bob, amount).transact(from_creator)
        t.functions.approve(y.address, amount).transact(from_bob)
        y.functions.deposit(amount).transact(from_bob)
        # Check according to definition
        assert y.caller.balanceOf(bob) * y.caller.getPricePerFullShare() // 10 ** 18 == amount
        # Tweak exchange rate
        y.functions.set_exchange_rate(y.caller.getPricePerFullShare() * 6 // 5).transact(from_creator)
        # Get back
        y.functions.withdraw(y.caller.balanceOf(bob)).transact(from_bob)
        assert t.caller.balanceOf(bob) == amount * 6 // 5
        assert y.caller.balanceOf(bob) == 0
