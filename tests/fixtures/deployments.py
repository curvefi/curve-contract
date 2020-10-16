import pytest
from brownie import Contract

from scripts.utils import right_pad, pack_values

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def _swap(project, alice, underlying, wrapped, pool_token, pool_data, swap_mock, base_swap):
    deployer = getattr(project, pool_data['swap_contract'])

    abi = next(i['inputs'] for i in deployer.abi if i['type'] == "constructor")
    args = {
        '_coins': wrapped,
        '_underlying_coins': underlying,
        '_pool_token': pool_token,
        '_base_pool': base_swap,
        '_A': 360 * 2,
        '_fee': 0,
        '_admin_fee': 0,
        '_offpeg_fee_multiplier': 0,
        '_owner': alice,
        '_y_pool': swap_mock,
    }
    deployment_args = [args[i['name']] for i in abi] + [({'from': alice})]

    contract = deployer.deploy(*deployment_args)
    pool_token.set_minter(contract, {'from': alice})

    return contract


@pytest.fixture(scope="module")
def swap(project, alice, _underlying_coins, wrapped_coins, pool_token, pool_data, swap_mock, base_swap):
    return _swap(project, alice, _underlying_coins, wrapped_coins, pool_token, pool_data, swap_mock, base_swap)


@pytest.fixture(scope="module")
def base_swap(project, charlie, _base_coins, base_pool_token, base_pool_data, is_forked):
    if base_pool_data is None:
        return
    if is_forked:
        return Contract(base_pool_data["swap_address"])
    return _swap(project, charlie, _base_coins, _base_coins, base_pool_token, base_pool_data, None, None)


@pytest.fixture(scope="module")
def swap_mock(SwapMock, pool_data, alice):
    if pool_data['name'] == "snow":
        return SwapMock.deploy({'from': alice})


@pytest.fixture(scope="module")
def zap(project, alice, swap, underlying_coins, wrapped_coins, pool_token, pool_data):
    deployer = getattr(project, pool_data.get('zap_contract'), None)
    if deployer is None:
        return

    abi = next(i['inputs'] for i in deployer.abi if i['type'] == "constructor")
    args = {
        '_coins': wrapped_coins,
        '_underlying_coins': underlying_coins,
        '_token': pool_token,
        '_pool': swap,
        '_curve': swap,
    }
    deployment_args = [args[i['name']] for i in abi] + [({'from': alice})]

    return deployer.deploy(*deployment_args)


@pytest.fixture(scope="module")
def registry(
    Registry,
    alice,
    gauge_controller,
    swap,
    pool_token,
    n_coins,
    underlying_decimals,
    wrapped_coins,
    wrapped_decimals,
    pool_data,
):
    registry = Registry.deploy(gauge_controller, {'from': alice})

    rate_sig = "0x00"
    if next((i for i in wrapped_coins if hasattr(i, "get_rate")), False):
        contract = next(i for i in wrapped_coins if hasattr(i, "get_rate"))
        rate_sig = right_pad(contract.get_rate.signature)
    has_initial_A = hasattr(swap, "initial_A")
    is_v1 = pool_data['lp_contract'] == "CurveTokenV1"

    if hasattr(swap, "underlying_coins"):
        registry.add_pool(
            swap,
            n_coins,
            pool_token,
            ZERO_ADDRESS,
            rate_sig,
            pack_values(wrapped_decimals),
            pack_values(underlying_decimals),
            has_initial_A,
            is_v1,
            {'from': alice}
        )
    else:
        use_rates = ['wrapped_decimals' in i for i in pool_data['coins']] + [False] * (8 - n_coins)
        registry.add_pool_without_underlying(
            swap,
            n_coins,
            pool_token,
            ZERO_ADDRESS,
            rate_sig,
            pack_values(underlying_decimals),
            pack_values(use_rates),
            has_initial_A,
            is_v1,
            {'from': alice}
        )

    return registry


@pytest.fixture(scope="module")
def gauge_controller(GaugeControllerMock, alice):
    return GaugeControllerMock.deploy({'from': alice})
