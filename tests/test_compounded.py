def test_cerc20(w3, coins, cerc20s):
    from_creator = {'from': w3.eth.accounts[0]}
    bob = w3.eth.accounts[1]
    from_bob = {'from': bob}
    for t, c in zip(coins, cerc20s):
        amount = 10 ** 5 * 10 ** t.caller.decimals()
        t.functions.transfer(bob, amount).transact(from_creator)
        t.functions.approve(c.address, amount).transact(from_bob)
        c.functions.mint(amount).transact(from_bob)
        # Check according to definition
        assert c.caller.balanceOf(bob) * c.caller.exchangeRateStored() // 10 ** 18 == amount
        # Tweak exchange rate
        c.functions.set_exchange_rate(c.caller.exchangeRateStored() * 6 // 5).transact(from_creator)
        # Get back
        c.functions.redeem(c.caller.balanceOf(bob)).transact(from_bob)
        assert t.caller.balanceOf(bob) == amount * 6 // 5
        assert c.caller.balanceOf(bob) == 0
