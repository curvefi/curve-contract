from .conftest import UU


def test_erc20(w3, coins):
    for c, U in zip(coins, UU):
        assert c.caller.totalSupply() == 10 ** 9 * U
