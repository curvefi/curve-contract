def test_erc20(w3, erc20):
    assert erc20.totalSupply() == 10 ** 9 * 10 ** 18
