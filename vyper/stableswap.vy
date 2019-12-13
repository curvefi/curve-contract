import ERC20m as ERC20m
import cERC20 as cERC20

# This can (and needs to) be changed at compile time
N_COINS: constant(int128) = 3  # <- change

ZERO256: constant(uint256) = 0  # This hack is really bad XXX
ZEROS: constant(uint256[N_COINS]) = [ZERO256, ZERO256, ZERO256]  # <- change

PRECISION: constant(uint256) = 10 ** 18  # The precision to convert to
PRECISION_MUL: constant(uint256[N_COINS]) = [
    PRECISION / convert(10 ** 18, uint256),  # DAI
    PRECISION / convert(10 ** 6, uint256),   # USDC
    PRECISION / convert(10 ** 6, uint256)]   # USDT
# PRECISION_MUL: constant(uint256[N_COINS]) = [
#     convert(1, uint256),
#     convert(1, uint256),
#     convert(1, uint256)]

admin_actions_delay: constant(uint256) = 7 * 86400

# Events
TokenExchange: event({buyer: indexed(address), sold_id: int128, tokens_sold: uint256, bought_id: int128, tokens_bought: uint256, fee: uint256})
AddLiquidity: event({provider: indexed(address), token_amounts: uint256[N_COINS]})
RemoveLiquidity: event({provider: indexed(address), token_amounts: uint256[N_COINS], fees: uint256[N_COINS]})
CommitNewAdmin: event({deadline: indexed(timestamp), admin: indexed(address)})
NewAdmin: event({admin: indexed(address)})
CommitNewParameters: event({deadline: indexed(timestamp), A: int128, fee: int128, admin_fee: int128})
NewParameters: event({A: int128, fee: int128, admin_fee: int128})

coins: public(address[N_COINS])
balances: public(uint256[N_COINS])
A: public(int128)  # 2 x amplification coefficient
fee: public(int128)  # fee * 1e10
admin_fee: public(int128)  # admin_fee * 1e10
max_admin_fee: constant(int128) = 5 * 10 ** 9

owner: public(address)
token: ERC20m

admin_actions_deadline: public(timestamp)
transfer_ownership_deadline: public(timestamp)
future_A: public(int128)
future_fee: public(int128)
future_admin_fee: public(int128)
future_owner: public(address)


@public
def __init__(_coins: address[N_COINS], _pool_token: address,
             _A: int128, _fee: int128):
    for i in range(N_COINS):
        assert _coins[i] != ZERO_ADDRESS
        self.balances[i] = 0
    self.coins = _coins
    self.A = _A
    self.fee = _fee
    self.admin_fee = 0
    self.owner = msg.sender
    self.token = ERC20m(_pool_token)


@private
@constant
def _rates() -> uint256[N_COINS]:
    result: uint256[N_COINS] = PRECISION_MUL
    for i in range(N_COINS):
        rate: uint256 = cERC20(self.coins[i]).exchangeRateStored()
        result[i] = rate * result[i]
    return result


@private
@constant
def _xp_raw(rates: uint256[N_COINS]) -> uint256[N_COINS]:
    result: uint256[N_COINS] = rates
    for i in range(N_COINS):
        result[i] = result[i] * self.balances[i] / 10 ** 18
    return result


@private
@constant
def _xp() -> uint256[N_COINS]:
    return self._xp_raw(self._rates())


@private
@constant
def get_D(xp: uint256[N_COINS]) -> uint256:
    S: uint256 = 0
    for _x in xp:
        S += _x
    if S == 0:
        return 0

    Dprev: uint256 = 0
    D: uint256 = S
    Ann: uint256 = convert(self.A, uint256) * N_COINS
    for _i in range(255):
        D_P: uint256 = D
        for _x in xp:
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
    # Amounts is amounts of c-tokens
    assert block.timestamp <= deadline, "Transaction expired"

    token_supply: uint256 = self.token.totalSupply()
    # Initial invariant
    D0: uint256 = 0
    if token_supply > 0:
        D0 = self.get_D(self._xp())

    for i in range(N_COINS):
        # Check for allowances before any transfers or calculations
        assert_modifiable(
            cERC20(self.coins[i]).balanceOf(msg.sender) >= amounts[i])
        assert_modifiable(
            cERC20(self.coins[i]).allowance(msg.sender, self) >= amounts[i])
        if token_supply == 0:
            assert amounts[i] > 0
        # balances store amounts of c-tokens
        self.balances[i] += amounts[i]

    # Invariant after change
    D1: uint256 = self.get_D(self._xp())
    assert D1 > D0

    # Calculate, how much pool tokens to mint
    mint_amount: uint256 = 0
    if token_supply == 0:
        mint_amount = D1  # Take the dust if there was any
    else:
        mint_amount = token_supply * (D1 - D0) / D0

    # Take coins from the sender
    for i in range(N_COINS):
        assert_modifiable(
            cERC20(self.coins[i]).transferFrom(msg.sender, self, amounts[i]))

    # Mint pool tokens
    self.token.mint(msg.sender, mint_amount)

    log.AddLiquidity(msg.sender, amounts)


@private
@constant
def get_y(i: int128, j: int128, x: uint256, _xp: uint256[N_COINS]) -> uint256:
    # x in the input is converted to the same price/precision
    D: uint256 = self.get_D(_xp)
    c: uint256 = D
    S_: uint256 = 0
    Ann: uint256 = convert(self.A, uint256) * N_COINS

    _x: uint256 = 0
    for _i in range(N_COINS):
        if _i == i:
            _x = x
        elif _i != j:
            _x = _xp[_i]
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
    # dx and dy in c-units
    rates: uint256[N_COINS] = self._rates()
    xp: uint256[N_COINS] = self._xp_raw(rates)

    x: uint256 = xp[i] + dx * rates[i] / 10 ** 18
    y: uint256 = self.get_y(i, j, x, xp)
    return (xp[j] - y) * 10 ** 18 / rates[j]


@public
@nonreentrant('lock')
def exchange(i: int128, j: int128, dx: uint256,
             min_dy: uint256, deadline: timestamp):
    assert block.timestamp <= deadline, "Transaction expired"
    assert i < N_COINS and j < N_COINS, "Coin number out of range"
    # dx and dy are in c-tokens

    rates: uint256[N_COINS] = self._rates()
    xp: uint256[N_COINS] = self._xp_raw(rates)

    x: uint256 = xp[i] + dx * rates[i] / 10 ** 18
    y: uint256 = self.get_y(i, j, x, xp)
    dy: uint256 = xp[j] - y
    dy_fee: uint256 = dy * convert(self.fee, uint256) / 10 ** 10
    dy_admin_fee: uint256 = dy_fee * convert(self.admin_fee, uint256) / 10 ** 10
    self.balances[i] = x * 10 ** 18 / rates[i]
    self.balances[j] = (y + (dy_fee - dy_admin_fee)) * 10 ** 18 / rates[j]

    _dy: uint256 = (dy - dy_fee) * 10 ** 18 / rates[j]
    assert _dy >= min_dy

    assert_modifiable(cERC20(self.coins[i]).transferFrom(msg.sender, self, dx))
    assert_modifiable(cERC20(self.coins[j]).transfer(msg.sender, _dy))

    log.TokenExchange(msg.sender, i, dx, j, _dy, dy_fee * 10 ** 18 / rates[j])

    # If needed, redepmption should happen as an external call


@public
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, deadline: timestamp,
                     min_amounts: uint256[N_COINS]):
    assert block.timestamp <= deadline, "Transaction expired"
    assert self.token.balanceOf(msg.sender) >= _amount
    assert self.token.allowance(msg.sender, self) >= _amount
    total_supply: uint256 = self.token.totalSupply()
    amounts: uint256[N_COINS] = ZEROS
    fees: uint256[N_COINS] = ZEROS

    for i in range(N_COINS):
        value: uint256 = self.balances[i] * _amount / total_supply
        assert value >= min_amounts[i]
        self.balances[i] -= value
        amounts[i] = value
        assert_modifiable(cERC20(self.coins[i]).transfer(
            msg.sender, value))

    self.token.burnFrom(msg.sender, _amount)

    log.RemoveLiquidity(msg.sender, amounts, fees)


@public
@nonreentrant('lock')
def remove_liquidity_imbalance(amounts: uint256[N_COINS], deadline: timestamp):
    assert block.timestamp <= deadline, "Transaction expired"

    rates: uint256[N_COINS] = self._rates()
    xp: uint256[N_COINS] = self._xp_raw(rates)
    token_supply: uint256 = self.token.totalSupply()
    assert token_supply > 0
    fees: uint256[N_COINS] = ZEROS
    _fee: uint256 = convert(self.fee, uint256)
    _admin_fee: uint256 = convert(self.admin_fee, uint256)

    D0: uint256 = self.get_D(xp)
    for i in range(N_COINS):
        fees[i] = amounts[i] * _fee / 10 ** 10
        self.balances[i] -= amounts[i] + fees[i]  # Charge all fees
    D1: uint256 = self.get_D(self._xp())

    token_amount: uint256 = (D0 - D1) * token_supply / D0
    assert self.token.balanceOf(msg.sender) >= token_amount
    assert self.token.allowance(msg.sender, self) >= token_amount
    for i in range(N_COINS):
        assert_modifiable(cERC20(self.coins[i]).transfer(msg.sender, amounts[i]))
    self.token.burnFrom(msg.sender, token_amount)

    # Now "charge" fees
    # In fact, we "refund" fees to the liquidity providers but w/o admin fees
    # They got paid by burning a higher amount of liquidity token from sender
    for i in range(N_COINS):
        self.balances[i] += fees[i] - _admin_fee * fees[i] / 10 ** 10

    log.RemoveLiquidity(msg.sender, amounts, fees)


### Admin functions ###
@public
def commit_new_parameters(amplification: int128,
                          new_fee: int128,
                          new_admin_fee: int128):
    assert msg.sender == self.owner
    assert self.admin_actions_deadline == 0
    assert new_admin_fee <= max_admin_fee

    _deadline: timestamp = block.timestamp + admin_actions_delay
    self.admin_actions_deadline = _deadline
    self.future_A = amplification
    self.future_fee = new_fee
    self.future_admin_fee = new_admin_fee

    log.CommitNewParameters(_deadline, amplification, new_fee, new_admin_fee)


@public
def apply_new_parameters():
    assert msg.sender == self.owner
    assert self.admin_actions_deadline <= block.timestamp\
        and self.admin_actions_deadline > 0

    self.admin_actions_deadline = 0
    _A: int128 = self.future_A
    _fee: int128 = self.future_fee
    _admin_fee: int128 = self.future_admin_fee
    self.A = _A
    self.fee = _fee
    self.admin_fee = _admin_fee

    log.NewParameters(_A, _fee, _admin_fee)


@public
def revert_new_parameters():
    assert msg.sender == self.owner

    self.admin_actions_deadline = 0


@public
def commit_transfer_ownership(_owner: address):
    assert msg.sender == self.owner
    assert self.transfer_ownership_deadline == 0

    _deadline: timestamp = block.timestamp + admin_actions_delay
    self.transfer_ownership_deadline = _deadline
    self.future_owner = _owner

    log.CommitNewAdmin(_deadline, _owner)


@public
def apply_transfer_ownership():
    assert msg.sender == self.owner
    assert block.timestamp >= self.transfer_ownership_deadline\
        and self.transfer_ownership_deadline > 0

    self.transfer_ownership_deadline = 0
    _owner: address = self.future_owner
    self.owner = _owner

    log.NewAdmin(_owner)


@public
def revert_transfer_ownership():
    assert msg.sender == self.owner

    self.transfer_ownership_deadline = 0


@public
def withdraw_admin_fees():
    assert msg.sender == self.owner
    _precisions: uint256[N_COINS] = PRECISION_MUL

    for i in range(N_COINS):
        c: address = self.coins[i]
        value: uint256 = cERC20(c).balanceOf(self) - self.balances[i] / _precisions[i]
        if value > 0:
            assert_modifiable(cERC20(c).transfer(msg.sender, value))
