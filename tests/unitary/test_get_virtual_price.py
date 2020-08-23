import pytest

from tests.conftest import PRECISIONS

INITIAL_AMOUNTS = [10**(i+6) for i in PRECISIONS]
MAX_FEE = 5 * 10**9


@pytest.fixture(scope="module", autouse=True)
def setup(chain, alice, coins, swap):
    for coin, amount in zip(coins, INITIAL_AMOUNTS):
        coin._mint_for_testing(alice, amount, {'from': alice})
        coin.approve(swap, 2**256-1, {'from': alice})

    swap.add_liquidity(INITIAL_AMOUNTS, 0, {'from': alice})

    swap.commit_new_fee(MAX_FEE, MAX_FEE, {'from': alice})
    chain.sleep(86400*3)
    swap.apply_new_fee({'from': alice})


def test_initial(swap):
    assert swap.get_virtual_price() == 10**18


@pytest.mark.parametrize("idx", range(len(INITIAL_AMOUNTS)))
def test_add_imbalanced_liquidity(alice, swap, coins, idx):
    amounts = [0, 0]
    amounts[idx] = INITIAL_AMOUNTS[idx]
    coins[idx]._mint_for_testing(alice, amounts[idx], {'from': alice})
    swap.add_liquidity(amounts, 0, {'from': alice})

    assert 1.04 < swap.get_virtual_price() / 10**18 < 1.05
