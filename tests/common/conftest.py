import pytest

# helper functions for contract interactions where the functionality differs
# depending on the pool


@pytest.fixture
def get_admin_balances(swap, wrapped_coins):

    def _get_admin_balances():
        admin_balances = []
        for i, coin in enumerate(wrapped_coins):
            if hasattr(swap, "admin_balances"):
                admin_balances.append(swap.admin_balances(i))
            else:
                admin_balances.append(coin.balanceOf(swap) - swap.balances(i))

        return admin_balances

    yield _get_admin_balances


@pytest.fixture(scope="module")
def set_fees(chain, alice, swap):
    def _set_fees(fee, admin_fee):
        if hasattr(swap, "commit_new_fee"):
            swap.commit_new_fee(fee, admin_fee, {'from': alice})
            chain.sleep(86400*3)
            swap.apply_new_fee({'from': alice})
        else:
            swap.commit_new_parameters(360 * 2, fee, admin_fee, {'from': alice})
            chain.sleep(86400*3)
            swap.apply_new_parameters({'from': alice})

    yield _set_fees
