import pytest

MAX_FEE = 5 * 10**9


@pytest.fixture(scope="module", autouse=True)
def setup(chain, alice, wrapped_coins, swap, initial_amounts, set_fees):
    for coin, amount in zip(wrapped_coins, initial_amounts):
        coin._mint_for_testing(alice, amount * 2, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})

    swap.add_liquidity(initial_amounts, 0, {'from': alice})
    set_fees(MAX_FEE, MAX_FEE)


def test_initial(swap):
    assert swap.get_virtual_price() == 10**18


def test_number_go_up(alice, swap, initial_amounts, n_coins):
    virtual_price = swap.get_virtual_price()

    for i, amount in enumerate(initial_amounts):
        amounts = [0] * n_coins
        amounts[i] = amount
        swap.add_liquidity(amounts, 0, {'from': alice})

        new_virtual_price = swap.get_virtual_price()
        assert new_virtual_price > virtual_price
        virtual_price = new_virtual_price
