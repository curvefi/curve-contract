import pytest

MAX_FEE = 5 * 10**9


@pytest.fixture(scope="module", autouse=True)
def setup(add_initial_liquidity, approve_bob, mint_bob, set_fees):
    set_fees(MAX_FEE, MAX_FEE)


def test_initial(swap):
    assert swap.get_virtual_price() == 10**18


def test_number_go_up(bob, swap, initial_amounts, n_coins):
    virtual_price = swap.get_virtual_price()

    for i, amount in enumerate(initial_amounts):
        amounts = [0] * n_coins
        amounts[i] = amount
        swap.add_liquidity(amounts, 0, {'from': bob})

        new_virtual_price = swap.get_virtual_price()
        assert new_virtual_price > virtual_price
        virtual_price = new_virtual_price
