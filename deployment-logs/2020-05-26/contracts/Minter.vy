contract Controller:
    def gauges(gauge_id: int128) -> address: constant

contract Gauge:
    # Presumably, other gauges will provide the same interfaces
    def integrate_fraction(addr: address) -> uint256: constant
    def user_checkpoint(addr: address): modifying

contract MERC20:
    def mint(_to: address, _value: uint256): modifying


token: public(address)
controller: public(address)

minted: public(map(address, map(address, uint256)))  # user -> gauge -> value


@public
def __init__(_token: address, _controller: address):
    self.token = _token
    self.controller = _controller


@public
@nonreentrant('lock')
def mint(gauge_id: int128):
    """
    Mint everything which belongs to msg.sender and send to them
    """
    gauge_addr: address = Controller(self.controller).gauges(gauge_id)
    assert gauge_addr != ZERO_ADDRESS, "Gauge is not in controller"

    Gauge(gauge_addr).user_checkpoint(msg.sender)
    total_mint: uint256 = Gauge(gauge_addr).integrate_fraction(msg.sender)
    to_mint: uint256 = total_mint - self.minted[msg.sender][gauge_addr]

    if to_mint > 0:
        MERC20(self.token).mint(msg.sender, to_mint)
        self.minted[msg.sender][gauge_addr] = total_mint
