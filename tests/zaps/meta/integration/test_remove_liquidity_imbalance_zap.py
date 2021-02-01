import pytest
from brownie.test import given, strategy
from hypothesis import settings


@pytest.fixture(scope="module", autouse=True)
def setup(alice, bob, pool_token, add_initial_liquidity, approve_zap, set_fees):
    pool_token.transfer(bob, pool_token.balanceOf(alice), {"from": alice})
    set_fees(4000000, 5000000000, include_meta=True)


@given(
    st_base=strategy("decimal[3]", min_value=0, max_value="0.49", unique=True, places=2),
    st_zap=strategy("decimal[4]", min_value=0, max_value="0.99", unique=True, places=2),
)
@settings(max_examples=100)
def test_remove_liquidity_imbalance(
    bob, charlie, zap, pool_token, initial_amounts_underlying, base_swap, swap, st_base, st_zap
):

    # remove liquidity from base pool to leave it imbalanced
    # st_base maxes at 49% because 50% of the total supply is with charlie
    amounts = [int(base_swap.balances(i) * st_base[i]) for i in range(3)]
    base_swap.remove_liquidity_imbalance(amounts, 2 ** 256 - 1, {"from": charlie})

    # attempt an imbalanced withdrawal from the base pool via the metapool zap
    amounts = [int(initial_amounts_underlying[i] * st_zap[i]) for i in range(4)]
    max_burn = pool_token.balanceOf(bob)

    # we aren't worried about the amounts here, just that the function does not revert
    zap.remove_liquidity_imbalance(amounts, max_burn, {"from": bob})
