from vyper.interfaces import ERC20
import ERC20m as ERC20m

# This can (and needs to) be changed at compile time
N_COINS: constant(int128) = 3
Z256: constant(uint256) = 0
ZEROS256: constant(uint256[3]) = [Z256, Z256, Z256]
admin_actions_delay: constant(uint256) = 7 * 86400

coins: public(address[N_COINS])
balances: public(uint256[N_COINS])
A: public(int128)  # 2 x amplification coefficient
fee: public(int128)  # fee * 1e10
admin_fee: public(int128)  # admin_fee * 1e10
max_admin_fee: constant(int128) = 5 * 10 ** 9

owner: public(address)
token: ERC20m

admin_actions_deadline: public(uint256)
transfer_ownership_time: public(uint256)
future_A: public(int128)
future_fee: public(int128)
future_admin_fee: public(int128)
future_owner: public(address)


@public
def __init__(_coins: address[N_COINS], _pool_token: address,
             _A: int128, _fee: int128):
    for i in range(N_COINS):
        assert _coins[i] != ZERO_ADDRESS
    self.coins = _coins
    self.A = _A
    self.fee = _fee
    self.admin_fee = 0
    self.owner = msg.sender
    self.token = ERC20(_pool_token)


@private
@constant
def get_D() -> uint256:
    S: uint256 = 0
    for _x in self.balances:
        S += _x
    if S == 0:
        return 0

    Dprev: uint256 = 0
    D: uint256 = S
    Ann: uint256 = convert(self.A, uint256) * N_COINS
    for _i in range(255):
        D_P: uint256 = D
        for _x in self.balances:
            D_P = D_P * D / (_x * N_COINS + 1)  # +1 is to prevent /0
        Dprev = D
        D = (Ann * S + D_P * N_COINS) * D / ((Ann - 1) * D + (N_COINS + 1) * D_P)
        # Equality with the precision of 1
        if D > Dprev:
            if D - Dprev <= 1:
                break
        else:
            if Dprev - D <= 1:
                break
    return D


@public
@nonreentrant('lock')
def add_liquidity(amounts: uint256[N_COINS], deadline: timestamp):
    assert block.timestamp <= deadline, "Transaction expired"

    token_supply: uint256 = self.token.totalSupply()
    # Initial invariant
    D0: uint256
    if token_supply > 0:
        D0 = self.get_D()
    else:
        D0 = 0

    for i in range(N_COINS):
        # Check for allowances before any transfers or calculations
        assert_modifiable(
            ERC20(self.coins[i]).balanceOf(msg.sender) >= amounts[i])
        assert_modifiable(
            ERC20(self.coins[i]).allowance(msg.sender, self) >= amounts[i])
        if token_supply == 0:
            assert amounts[i] > 0
        self.balances[i] += amounts[i]

    # Invariant after change
    D1: uint256 = self.get_D()
    assert D1 > D0

    # Calculate, how much pool tokens to mint
    mint_amount: uint256
    if token_supply == 0:
        mint_amount = D1  # Take the dust if there was any
    else:
        mint_amount = token_supply * (D1 - D0) / D0

    # Take coins from the sender
    for i in range(N_COINS):
        assert_modifiable(
            ERC20(self.coins[i]).transferFrom(msg.sender, self, amounts[i]))

    # Mint pool tokens
    self.token.mint(msg.sender, mint_amount)


@private
@constant
def get_y(i: int128, j: int128, x: uint256) -> uint256:
    D: uint256 = self.get_D()
    c: uint256 = D
    S_: uint256 = 0
    Ann: uint256 = convert(self.A, uint256) * N_COINS
    for _i in range(N_COINS):
        _x: uint256
        if _i == i:
            _x = x
        elif _i != j:
            _x = self.balances[_i]
        else:
            continue
        S_ += _x
        c = c * D / (_x * N_COINS)
    c = c * D / (Ann * N_COINS)
    b: uint256 = S_ + D / Ann  # - D
    y_prev: uint256 = 0
    y: uint256 = D
    for _i in range(255):
        y_prev = y
        y = (y*y + c) / (2 * y + b - D)
        # Equality with the precision of 1
        if y > y_prev:
            if y - y_prev <= 1:
                break
        else:
            if y_prev - y <= 1:
                break
    return y


@public
@constant
def get_dy(i: int128, j: int128, dx: uint256) -> uint256:
    x: uint256 = self.balances[i] + dx
    y: uint256 = self.get_y(i, j, x)
    return self.balances[j] - y


@public
@nonreentrant('lock')
def exchange(i: int128, j: int128, dx: uint256,
             min_dy: uint256, deadline: timestamp):
    assert block.timestamp <= deadline, "Transaction expired"
    assert i < N_COINS and j < N_COINS, "Coin number out of range"

    x: uint256 = self.balances[i] + dx
    y: uint256 = self.get_y(i, j, x)
    dy: uint256 = self.balances[j] - y
    dy_fee: uint256 = dy * convert(self.fee, uint256) / 10 ** 10
    dy_admin_fee: uint256 = dy_fee * convert(self.admin_fee, uint256) / 10 ** 10
    self.balances[i] += dx
    self.balances[j] = y + (dy_fee - dy_admin_fee)

    assert_modifiable(ERC20(self.coins[i]).transferFrom(msg.sender, self, dx))
    assert_modifiable(ERC20(self.coins[j]).transfer(msg.sender, dy - dy_fee))


@public
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, deadline: timestamp,
                     min_amounts: uint256[N_COINS]):
    assert block.timestamp <= deadline, "Transaction expired"
    assert self.token.balanceOf(msg.sender) >= _amount
    assert self.token.allowance(msg.sender, self) >= _amount
    total_supply: uint256 = self.token.totalSupply()

    for i in range(N_COINS):
        value: uint256 = self.balances[i] * _amount / total_supply
        assert value >= min_amounts[i]
        self.balances[i] -= value
        assert_modifiable(ERC20(self.coins[i]).transfer(msg.sender, value))

    self.token.burnFrom(msg.sender, _amount)


@public
@nonreentrant('lock')
def remove_liquidity_imbalance(amounts: uint256[N_COINS], deadline: timestamp):
    assert block.timestamp <= deadline, "Transaction expired"

    token_supply: uint256 = self.token.totalSupply()
    assert token_supply > 0
    fees: uint256[N_COINS]
    _fee: uint256 = convert(self.fee, uint256)
    _admin_fee: uint256 = convert(self.admin_fee, uint256)
    D0: uint256 = self.get_D()
    for i in range(N_COINS):
        fees[i] = amounts[i] * _fee / 10 ** 10
        self.balances[i] -= amounts[i] + fees[i]  # Charge all fees
    D1: uint256 = self.get_D()

    token_amount: uint256 = (D0 - D1) * token_supply / D0
    assert self.token.balanceOf(msg.sender) >= token_amount
    assert self.token.allowance(msg.sender, self) >= token_amount
    for i in range(N_COINS):
        assert_modifiable(ERC20(self.coins[i]).transfer(msg.sender, amounts[i]))
    self.token.burnFrom(msg.sender, token_amount)

    # Now "charge" fees
    # In fact, we "refund" fees to the liquidity providers but w/o admin fees
    # They got paid by burning a higher amount of liquidity token from sender
    for i in range(N_COINS):
        self.balances[i] += fees[i] - _admin_fee * fees[i] / 10 ** 10
