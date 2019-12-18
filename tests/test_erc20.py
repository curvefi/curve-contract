from .conftest import UU


def test_erc20(w3, coins):
    for c, u in zip(coins, UU):
        assert c.caller.totalSupply() == 10 ** 12 * u
