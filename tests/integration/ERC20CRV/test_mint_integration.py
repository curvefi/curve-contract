import brownie
from brownie.test import strategy, given

from tests.conftest import YEAR


@given(duration=strategy('uint', min_value=1, max_value=YEAR))
def test_mint(accounts, chain, token, duration):
    token.set_minter(accounts[0], {'from': accounts[0]})
    creation_time = token.start_epoch_time()
    initial_supply = token.totalSupply()
    rate = token.rate()
    chain.sleep(duration)

    amount = (chain.time()-creation_time) * rate
    token.mint(accounts[1], amount, {'from': accounts[0]})

    assert token.balanceOf(accounts[1]) == amount
    assert token.totalSupply() == initial_supply + amount


@given(duration=strategy('uint', min_value=1, max_value=YEAR))
def test_overmint(accounts, chain, token, duration):
    token.set_minter(accounts[0], {'from': accounts[0]})
    creation_time = token.start_epoch_time()
    rate = token.rate()
    chain.sleep(duration)

    with brownie.reverts("dev: exceeds allowable mint amount"):
        token.mint(accounts[1], (chain.time()-creation_time+2) * rate, {'from': accounts[0]})


@given(durations=strategy('uint[5]', min_value=YEAR*0.33, max_value=YEAR*0.9))
def test_mint_multiple(accounts, chain, token, durations):
    token.set_minter(accounts[0], {'from': accounts[0]})
    total_supply = token.totalSupply()
    balance = 0
    epoch_start = token.start_epoch_time()

    for time in durations:
        chain.sleep(time)

        if chain.time() - epoch_start > YEAR:
            token.update_mining_parameters({'from': accounts[0]})
            epoch_start = token.start_epoch_time()

        amount = token.available_supply() - total_supply
        token.mint(accounts[1], amount, {'from': accounts[0]})

        balance += amount
        total_supply += amount

        assert token.balanceOf(accounts[1]) == balance
        assert token.totalSupply() == total_supply
