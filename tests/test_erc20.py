def test_erc20(w3, coin_a, coin_b):
    assert coin_a.totalSupply() == 10 ** 9 * 10 ** 18
    assert coin_b.totalSupply() == 10 ** 9 * 10 ** 18


def test_swap_is_there(swap):
    assert swap is not None
