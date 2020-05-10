from .conftest import UP


def test_yerc20(w3, yerc20s):
    for u, y in zip(UP, yerc20s):
        assert y.caller.decimals() == u
