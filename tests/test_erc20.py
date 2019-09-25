def test_erc20(w3, coins):
    for c in coins:
        assert c.caller.totalSupply() == 10 ** 9 * 10 ** 18
