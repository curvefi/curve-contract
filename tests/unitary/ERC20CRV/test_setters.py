import brownie


def test_set_minter_admin_only(accounts, token):
    with brownie.reverts("dev: admin only"):
        token.set_minter(accounts[2], {'from': accounts[1]})


def test_set_admin_admin_only(accounts, token):
    with brownie.reverts("dev: admin only"):
        token.set_admin(accounts[2], {'from': accounts[1]})


def test_set_name_admin_only(accounts, token):
    with brownie.reverts("Only admin is allowed to change name"):
        token.set_name("Foo Token", "FOO", {'from': accounts[1]})


def test_set_minter(accounts, token):
    token.set_minter(accounts[1], {'from': accounts[0]})

    assert token.minter() == accounts[1]


def test_set_admin(accounts, token):
    token.set_admin(accounts[1], {'from': accounts[0]})

    assert token.admin() == accounts[1]


def test_set_name(accounts, token):
    token.set_name("Foo Token", "FOO", {'from': accounts[0]})

    assert token.name() == "Foo Token"
    assert token.symbol() == "FOO"
