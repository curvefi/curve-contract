from vyper.interfaces import ERC20

coin_a: public(address)
coin_b: public(address)

@public
def __init__(a: address, b: address):
    assert a != ZERO_ADDRESS and b != ZERO_ADDRESS
    self.coin_a = a
    self.coin_b = b
