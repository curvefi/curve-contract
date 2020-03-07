from .conftest import UP


def test_yerc20(w3, yerc20s):
    for u, c in zip(UP, yerc20s):
        assert c.caller.decimals() == u
