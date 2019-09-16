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

owner: public(address)
admin_actions_delay: constant(uint256) = 7 * 86400

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
    pass

@public
def apply_new_parameters():
    pass

@public
def revert_new_parameters():
    pass

@public
def commit_transfer_ownership(_owner: address):
    pass

@public
def apply_transfer_ownership():
    pass

@public
def revert_transfer_ownership():
    pass
