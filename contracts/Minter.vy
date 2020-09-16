# @version 0.2.4

interface Gauge:
    # Presumably, other gauges will provide the same interfaces
    def integrate_fraction(addr: address) -> uint256: view
    def user_checkpoint(addr: address) -> bool: nonpayable

interface MERC20:
    def mint(_to: address, _value: uint256) -> bool: nonpayable

interface GaugeController:
    def gauge_types(addr: address) -> int128: view


token: public(address)
controller: public(address)

# user -> gauge -> value
minted: public(HashMap[address, HashMap[address, uint256]])


@external
def __init__(_token: address, _controller: address):
    self.token = _token
    self.controller = _controller


@external
@nonreentrant('lock')
def mint(gauge_addr: address):
    """
    Mint everything which belongs to msg.sender and send to them
    """
    assert GaugeController(self.controller).gauge_types(gauge_addr) >= 0  # dev: gauge is not added

    Gauge(gauge_addr).user_checkpoint(msg.sender)
    total_mint: uint256 = Gauge(gauge_addr).integrate_fraction(msg.sender)
    to_mint: uint256 = total_mint - self.minted[msg.sender][gauge_addr]

    if to_mint != 0:
        MERC20(self.token).mint(msg.sender, to_mint)
        self.minted[msg.sender][gauge_addr] = total_mint


# XXX change controller
