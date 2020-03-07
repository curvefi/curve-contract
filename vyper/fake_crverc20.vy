# Fake yERC20
#
# We should transfer tokens to _token_addr before wrapping
# in order to be able to get interest from somewhere
#
# WARNING
# This is for tests only and not meant to be safe to use


get_virtual_price: public(uint256)  # crvERC20 mock

@public
def __init__(exchange_rate: uint256):
    self.get_virtual_price = exchange_rate

@public
def set_exchange_rate(rate: uint256):
    self.get_virtual_price = rate
