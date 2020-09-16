import brownie

YEAR = 86400 * 365


def test_user_checkpoint(accounts, liquidity_gauge):
    liquidity_gauge.user_checkpoint(accounts[1], {'from': accounts[1]})


def test_user_checkpoint_new_period(accounts, chain, liquidity_gauge):
    liquidity_gauge.user_checkpoint(accounts[1], {'from': accounts[1]})
    chain.sleep(int(YEAR * 1.1))
    liquidity_gauge.user_checkpoint(accounts[1], {'from': accounts[1]})


def test_user_checkpoint_wrong_account(accounts, liquidity_gauge):
    with brownie.reverts("dev: unauthorized"):
        liquidity_gauge.user_checkpoint(accounts[2], {'from': accounts[1]})
