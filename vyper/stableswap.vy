from vyper.interfaces import ERC20

coin_a: public(address)
coin_b: public(address)

# Need to keep track of quantities of coins A and B separately
# because ability to send coins to shift equilibium may introduce a
# vulnerabilty
quantity_a: public(uint256)
quantity_b: public(uint256)

X: decimal  # "Amplification" coefficient
D: decimal  # "Target" quantity of coins in equilibrium

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
    self.coin_a = a
    self.coin_b = b
    self.X = convert(amplification, decimal)
    self.owner = msg.sender
    self.fee = convert(_fee, decimal) / 1e18
    self.admin_fee = 0

@public
def add_liquidity(coin_1: address, quantity_1: uint256,
                  max_quantity_2: uint256, deadline: timestamp):
    pass

@public
def remove_liquidity(coin_1: address, quantity_1: uint256,
                     max_quantity_2: uint256, deadline: timestamp):
    pass

@public
def get_price(from_coin: address, to_coin: address) -> uint256:
    return 0

@public
def get_volume(from_coin: address, to_coin: address,
               from_amount: uint256) -> uint256:
    return 0

@public
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
