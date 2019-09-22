from vyper.interfaces import ERC20

# This can (and needs to) be changed at compile time
N_COINS: constant(int128) = 3

coins: public(address[N_COINS])
balances: public(uint256[N_COINS])
A: public(int128)  # 2 x amplification coefficient
fee: public(int128)  # fee * 1e10
admin_fee: public(int128)  # admin_fee * 1e10
max_admin_fee: constant(int128) = 5 * 10 ** 9

owner: public(address)

admin_actions_delay: constant(uint256) = 7 * 86400
admin_actions_deadline: public(uint256)
transfer_ownership_deadline: public(uint256)
future_A: public(int128)
future_fee: public(int128)
future_admin_fee: public(int128)
future_owner: public(address)


@public
def __init__(_coins: address[N_COINS], _A: int128, _fee: int128):
    for i in range(N_COINS):
        assert _coins[i] != ZERO_ADDRESS
    self.coins = _coins
    self.A = _A
    self.fee = _fee
    self.admin_fee = 0
    self.owner = msg.sender


@public
@nonreentrant('lock')
def add_liquidity(i: int128, quantity_i: uint256,
                  max_quantity_other: uint256, deadline: timestamp):
    assert i < N_COINS
    assert block.timestamp <= deadline
    d_bal: uint256[N_COINS]

    for j in range(N_COINS):
        if j == i:
            d_bal[j] = quantity_i
        else:
            d_bal[j] = quantity_i * self.balances[j] / self.balances[i]
            assert d_bal[j] <= max_quantity_other
        assert ERC20(self.coins[j]).balanceOf(msg.sender) >= d_bal[j]
        assert ERC20(self.coins[j]).allowance(msg.sender, self) >= d_bal[j]

    ok: bool
    for j in range(N_COINS):
        ok = ERC20(self.coins[j]).transferFrom(msg.sender, self, d_bal[j])
        assert ok
