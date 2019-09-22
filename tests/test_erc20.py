def test_erc20(w3, coins):
    for c in coins:
        assert c.totalSupply() == 10 ** 9 * 10 ** 18


def test_swap_is_there(swap):
    assert swap is not None
