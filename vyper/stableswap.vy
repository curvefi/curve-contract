from vyper.interfaces import ERC20

coin_a: public(address)
coin_b: public(address)

# Need to keep track of quantities of coins A and B separately
# because ability to send coins to shift equilibium may introduce a
# vulnerabilty
quantity_a: public(uint256)
quantity_b: public(uint256)

X: decimal  # "Amplification" coefficient

fee: public(decimal)        # Fee for traders
admin_fee: public(decimal)  # Admin fee - fraction of fee
max_admin_fee: constant(decimal) = 0.5

owner: public(address)

admin_actions_delay: constant(uint256) = 7 * 86400
admin_actions_deadline: public(uint256)
transfer_ownership_deadline: public(uint256)
future_X: public(decimal)
future_fee: public(decimal)
future_admin_fee: public(decimal)
future_owner: public(address)

@public
def __init__(a: address, b: address,
             amplification: uint256, _fee: uint256):
    assert a != ZERO_ADDRESS and b != ZERO_ADDRESS
    # XXX TODO: use up 10 digits of decimal
    self.coin_a = a
    self.coin_b = b
    self.X = convert(amplification, decimal)
    self.owner = msg.sender
    self.fee = convert(_fee, decimal) / 1e18
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
def cbrt(x: decimal) -> decimal:
    """
    Cubic root by Babylonian Algotithm
        http://www.mathpath.org/Algor/cuberoot/cube.root.babylon.htm
    Inspired by Vyper implementation of sqrt
    """
    y: decimal = x
    z: decimal = (x + 1.0) / 2.0
    for i in range(256):
        if z == y:
            break
        y = z
        z = (2.0 * y + x / (y * y)) / 3.0
    return y

@private
@constant
def get_D() -> decimal:
    """
    Constant D by solving a cubic equation, using Cardano formula
    """
    x: decimal = convert(self.quantity_a, decimal)
    y: decimal = convert(self.quantity_b, decimal)
    A: decimal = self.X
    p: decimal = (16.0 * A - 4.0) * x * y
    q: decimal = -16.0 * A * x * y * (x + y)
    Disc: decimal = sqrt(q*q / 4.0 + p*p*p / 27.0)  # take xy out
    return self.cbrt(-q / 2.0 + Disc) - self.cbrt(q / 2.0 + Disc)  # and here
    # Gives about 1e20 - enough precision, hopefully?
    # Not compatible with hyper-inflation - too bad for Zimbabwe
    # Need to switch to integers also

@public
@constant
def get_price(from_coin: address, to_coin: address) -> decimal:
    if self.quantity_a == 0 and self.quantity_b == 0:
        return 1.0
    # XXX
    x: uint256 = 1000
    y: uint256 = sqrt256(x)
    return 1.0

@public
@constant
def get_volume(from_coin: address, to_coin: address,
               from_amount: uint256) -> uint256:
    x: decimal
    y: decimal
    if from_coin == self.coin_a and to_coin == self.coin_b:
        x = convert(self.quantity_a, decimal)
        y = convert(self.quantity_b, decimal)
    elif from_coin == self.coin_b and to_coin == self.coin_a:
        y = convert(self.quantity_a, decimal)
        x = convert(self.quantity_b, decimal)
    else:
        raise "Unknown coin"
    dx: decimal = convert(from_amount, decimal)
    return 0

@public
@nonreentrant('lock')
def exchange(from_coin: address, to_coin: address,
             from_amount: uint256, to_min_amount: uint256,
             deadline: timestamp):
    pass

@public
def commit_new_parameters(amplification: uint256,
                          new_fee: uint256,
                          new_admin_fee: uint256):
    assert msg.sender == self.owner
    assert self.admin_actions_deadline == 0

    self.admin_actions_deadline = as_unitless_number(block.timestamp) + admin_actions_delay
    self.future_X = convert(amplification, decimal)
    self.future_fee = convert(new_fee, decimal) / 1e18
    self.future_admin_fee = convert(new_admin_fee, decimal) / 1e18
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
