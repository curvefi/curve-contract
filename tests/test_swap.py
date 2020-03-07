from .conftest import UP


def test_swap(w3, swap):
    assert swap.caller.fee() == 10000000
