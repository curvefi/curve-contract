import brownie

WEEK = 86400 * 7
YEAR = 365 * 86400
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_available_supply(chain, web3, token):
    creation_time = token.start_epoch_time()
    initial_supply = token.totalSupply()
    rate = token.rate()
    chain.sleep(WEEK)
    chain.mine()

    expected = initial_supply + (chain[-1].timestamp - creation_time) * rate
    assert token.available_supply() == expected


def test_mint(accounts, chain, token):
    token.set_minter(accounts[0], {'from': accounts[0]})
    creation_time = token.start_epoch_time()
    initial_supply = token.totalSupply()
    rate = token.rate()
    chain.sleep(WEEK)

    amount = (chain.time()-creation_time) * rate
    token.mint(accounts[1], amount, {'from': accounts[0]})

    assert token.balanceOf(accounts[1]) == amount
    assert token.totalSupply() == initial_supply + amount


def test_overmint(accounts, chain, token):
    token.set_minter(accounts[0], {'from': accounts[0]})
    creation_time = token.start_epoch_time()
    rate = token.rate()
    chain.sleep(WEEK)

    with brownie.reverts("dev: exceeds allowable mint amount"):
        token.mint(accounts[1], (chain.time()-creation_time+2) * rate, {'from': accounts[0]})


def test_minter_only(accounts, token):
    token.set_minter(accounts[0], {'from': accounts[0]})
    with brownie.reverts("dev: minter only"):
        token.mint(accounts[1], 0, {'from': accounts[1]})


def test_zero_address(accounts, token):
    token.set_minter(accounts[0], {'from': accounts[0]})
    with brownie.reverts("dev: zero address"):
        token.mint(ZERO_ADDRESS, 0, {'from': accounts[0]})
