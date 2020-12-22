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


def _set_fees(chain, swap, fee, admin_fee, offpeg_multiplier=None):
    owner = swap.owner()
    if hasattr(swap, "commit_new_fee"):
        if hasattr(swap, "offpeg_fee_multiplier"):
            swap.commit_new_fee(fee, admin_fee, offpeg_multiplier or 0, {'from': owner})
        elif offpeg_multiplier is not None:
            raise ValueError("Pool does not support `offpeg_fee_multiplier`")
        else:
            swap.commit_new_fee(fee, admin_fee, {'from': owner})
        chain.sleep(86400*3)
        swap.apply_new_fee({'from': owner})
    else:
        swap.commit_new_parameters(360 * 2, fee, admin_fee, {'from': owner})
        chain.sleep(86400*3)
        swap.apply_new_parameters({'from': owner})



@pytest.fixture(scope="module")
def set_fees(chain, swap, base_swap):
    def _set_fee_fixture_fn(fee, admin_fee, include_meta=False):
        _set_fees(chain, swap, fee, admin_fee)
        if base_swap and include_meta:
            _set_fees(chain, base_swap, fee, admin_fee)

    yield _set_fee_fixture_fn


@pytest.fixture(scope="session")
def approx():

    def _approx(a, b, precision=1e-10):
        return 2 * abs(a - b) / (a + b) <= precision

    yield _approx
