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

@public
def __init__(a: address, b: address, x: uint256):
    assert a != ZERO_ADDRESS and b != ZERO_ADDRESS
    self.coin_a = a
    self.coin_b = b
    self.X = convert(x, decimal)
