from vyper.interfaces import ERC20

coin_a: public(address)
coin_b: public(address)

# Need to keep track of quantities of coins A and B separately
# because ability to send coins to shift equilibium may introduce a
# vulnerabilty
quantity_a: public(uint256)
quantity_b: public(uint256)

X: int128  # "Amplification" coefficient

fee: public(decimal)        # Fee for traders
admin_fee: public(decimal)  # Admin fee - fraction of fee
max_admin_fee: constant(decimal) = 0.5

owner: public(address)

admin_actions_delay: constant(uint256) = 7 * 86400
admin_actions_deadline: public(uint256)
transfer_ownership_deadline: public(uint256)
future_X: public(int128)
future_fee: public(decimal)
future_admin_fee: public(decimal)
future_owner: public(address)

@public
def __init__(a: address, b: address,
             amplification: int128, _fee: decimal):
    assert a != ZERO_ADDRESS and b != ZERO_ADDRESS
    self.coin_a = a
    self.coin_b = b
    self.X = 100
    self.owner = msg.sender
    self.fee = 0.001
    self.admin_fee = 0

@public
@nonreentrant('lock')
def add_liquidity(coin_1: address, quantity_1: uint256,
                  max_quantity_2: uint256, deadline: timestamp):
    assert coin_1 == self.coin_a or coin_1 == self.coin_b
    assert block.timestamp >= deadline

    A: address
    B: address
    quantity_2: uint256

    if coin_1 == self.coin_a:
        A = self.coin_a
        B = self.coin_b
    else:
        A = self.coin_b
        B = self.coin_a


    if coin_1 == self.coin_a:
        quantity_2 = quantity_1 * self.quantity_b / self.quantity_a
        self.quantity_a += quantity_1
        self.quantity_b += quantity_2
    else:
        quantity_2 = quantity_1 * self.quantity_a / self.quantity_b
        self.quantity_a += quantity_2
        self.quantity_b += quantity_1
    assert quantity_2 <= max_quantity_2

    ok: bool
    ok = ERC20(A).transferFrom(msg.sender, self, quantity_1)
    assert ok
    ok = ERC20(B).transferFrom(msg.sender, self, quantity_2)
    assert ok

@public
@nonreentrant('lock')
def remove_liquidity(coin_1: address, quantity_1: uint256,
                     min_quantity_2: uint256, deadline: timestamp):
    assert coin_1 == self.coin_a or coin_1 == self.coin_b
    assert block.timestamp >= deadline
    assert self.quantity_a > 0 and self.quantity_b > 0

    A: address
    B: address
    quantity_2: uint256

    if coin_1 == self.coin_a:
        A = self.coin_a
        B = self.coin_b
        quantity_2 = quantity_1 * self.quantity_b / self.quantity_a
        self.quantity_a -= quantity_1
        self.quantity_b -= quantity_2
    else:
        A = self.coin_b
        B = self.coin_a
        quantity_2 = quantity_1 * self.quantity_a / self.quantity_b
        self.quantity_a -= quantity_2
        self.quantity_b -= quantity_1

    assert quantity_2 >= min_quantity_2

    ok: bool
    ok = ERC20(A).transferFrom(self, msg.sender, quantity_1)
    assert ok
    ok = ERC20(B).transferFrom(self, msg.sender, quantity_2)
    assert ok

@private
@constant
def sqrt_int(x: uint256) -> uint256:
    y: uint256 = x
    z: uint256 = (x + 1) / 2
    for i in range(256):
        if z >= y:
            break
        y = z
        z = (y + x / y) / 2
    return y

@private
@constant
def cbrt_int(x: uint256) -> uint256:
    """
    Cubic root by Babylonian Algotithm
        http://www.mathpath.org/Algor/cuberoot/cube.root.babylon.htm
    Inspired by Vyper implementation of sqrt
    """
    y: uint256 = x
    z: uint256 = (x + 1) / 2
    for i in range(256):
        if z >= y:
            break
        y = z
        z = (2 * y + x / (y * y)) / 3
    return y

@private
@constant
def get_D() -> uint256:
    """
    Constant D by solving a cubic equation, using Cardano formula
    """
    # Gives about 1e20 - enough precision
    x: uint256 = self.quantity_a
    y: uint256 = self.quantity_b
    A: uint256 = convert(self.X, uint256)
    xy: uint256 = x * y
    p: uint256 = (16 * A - 4)  # * xy
    q: uint256 = 16 * A * (x + y)  # * xy
    Disc: uint256 = self.sqrt_int(q*q / 4 + p*p*p / 27)  # * xy
    xy = self.cbrt_int(xy)
    D: uint256 = self.cbrt_int(q / 2 + Disc) - self.cbrt_int(Disc - q / 2)
    return D * xy

@public
@constant
def get_price(from_coin: address, to_coin: address) -> decimal:
    if self.quantity_a == 0 and self.quantity_b == 0:
        return 1.0
    # XXX
    return 1.0

@public
@constant
def get_volume(from_coin: address, to_coin: address,
               from_amount: int128) -> int128:
    """
    Volume of buying of to_coin when using from_amount of from_coin
    """
    x: uint256
    y: uint256
    new_x: uint256
    new_y: uint256
    if from_coin == self.coin_a and to_coin == self.coin_b:
        x = self.quantity_a
        y = self.quantity_b
    elif from_coin == self.coin_b and to_coin == self.coin_a:
        y = self.quantity_a
        x = self.quantity_b
    else:
        raise "Unknown coin"
    if from_amount >= 0:
        new_x = x + convert(from_amount, uint256)
    else:
        new_x = x - convert(-from_amount, uint256)
    D: uint256 = self.get_D()
    A: uint256 = convert(self.X, uint256)
    Disc: uint256 = 16 * A * x - 4 * x - 16 * A * x*x / D
    Disc = self.sqrt_int(Disc*Disc + 64 * A * D * x)
    new_y = (D * Disc + 16 * A * D * x - 16 * A * x*x - 4 * D * x) / (32 * A * x)
    if from_amount >= 0:
        return convert(y - new_y, int128)
    else:
        return -convert(new_y - y, int128)

@public
@nonreentrant('lock')
def exchange(from_coin: address, to_coin: address,
             from_amount: uint256, to_min_amount: uint256,
             deadline: timestamp):
    pass

@public
def commit_new_parameters(amplification: int128,
                          new_fee: decimal,
                          new_admin_fee: decimal):
    assert msg.sender == self.owner
    assert self.admin_actions_deadline == 0

    self.admin_actions_deadline = as_unitless_number(block.timestamp) + admin_actions_delay
    self.future_X = amplification
    self.future_fee = new_fee
    self.future_admin_fee = new_admin_fee
    assert self.future_admin_fee < max_admin_fee

@public
def apply_new_parameters():
    assert msg.sender == self.owner
    assert self.admin_actions_deadline >= block.timestamp

    self.admin_actions_deadline = 0
    self.X = self.future_X
    self.fee = self.future_fee
    self.admin_fee = self.future_admin_fee

@public
def revert_new_parameters():
    assert msg.sender == self.owner

    self.admin_actions_deadline = 0

@public
def commit_transfer_ownership(_owner: address):
    assert msg.sender == self.owner
    assert self.transfer_ownership_deadline == 0

    self.transfer_ownership_deadline = as_unitless_number(block.timestamp) + admin_actions_delay
    self.future_owner = _owner

@public
def apply_transfer_ownership():
    assert msg.sender == self.owner
    assert self.transfer_ownership_deadline >= block.timestamp

    self.transfer_ownership_deadline = 0
    self.owner = self.future_owner

@public
def revert_transfer_ownership():
    assert msg.sender == self.owner

    self.transfer_ownership_deadline = 0
