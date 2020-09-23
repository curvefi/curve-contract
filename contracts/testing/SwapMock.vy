# @version ^0.2.0
# Minimal StableSwap mock for testing snow pool

virtual_price: uint256

@external
def __init__():
    self.virtual_price = 10 ** 18


@view
@external
def get_virtual_price() -> uint256:
    return self.virtual_price


@external
def _set_virtual_price(_value: uint256):
    self.virtual_price = _value
