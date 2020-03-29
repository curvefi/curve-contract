# A "zap" to deposit/withdraw Curve contract without too many transactions
from vyper.interfaces import ERC20
import cERC20 as cERC20


# Tether transfer-only ABI
contract USDT:
    def transfer(_to: address, _value: uint256): modifying
    def transferFrom(_from: address, _to: address, _value: uint256): modifying


contract Curve:
    def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256): modifying
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]): modifying
    def remove_liquidity_imbalance(amounts: uint256[N_COINS], max_burn_amount: uint256): modifying


N_COINS: constant(int128) = ___N_COINS___
TETHERED: constant(bool[N_COINS]) = ___TETHERED___
USE_LENDING: constant(bool[N_COINS]) = ___USE_LENDING___
ZERO256: constant(uint256) = 0  # This hack is really bad XXX
ZEROS: constant(uint256[N_COINS]) = ___N_ZEROS___  # <- change
LENDING_PRECISION: constant(uint256) = 10 ** 18

coins: public(address[N_COINS])
underlying_coins: public(address[N_COINS])
curve: public(address)
token: public(address)


@public
def __init__(_coins: address[N_COINS], _underlying_coins: address[N_COINS],
             _curve: address, _token: address):
    self.coins = _coins
    self.underlying_coins = _underlying_coins
    self.curve = _curve
    self.token = _token


@public
@nonreentrant('lock')
def add_liquidity(uamounts: uint256[N_COINS], min_mint_amount: uint256):
    use_lending: bool[N_COINS] = USE_LENDING
    tethered: bool[N_COINS] = TETHERED
    amounts: uint256[N_COINS] = ZEROS

    for i in range(N_COINS):
        uamount: uint256 = uamounts[i]

        # Transfer the underlying coin from owner
        if tethered[i]:
            USDT(self.underlying_coins[i]).transferFrom(
                msg.sender, self, uamount)
        else:
            assert_modifiable(ERC20(self.underlying_coins[i])\
                .transferFrom(msg.sender, self, uamount))

        # Mint if needed
        if use_lending[i]:
            ERC20(self.underlying_coins[i]).approve(self.coins[i], uamount)
            ok: uint256 = cERC20(self.coins[i]).mint(uamount)
            if ok > 0:
                raise "Could not mint coin"
            amounts[i] = cERC20(self.coins[i]).balanceOf(self)
            ERC20(self.coins[i]).approve(self.curve, amounts[i])
        else:
            amounts[i] = uamount
            ERC20(self.underlying_coins[i]).approve(self.curve, uamount)

    Curve(self.curve).add_liquidity(amounts, min_mint_amount)

    tokens: uint256 = ERC20(self.token).balanceOf(self)
    assert_modifiable(ERC20(self.token).transfer(msg.sender, tokens))


@private
def _send_all(_addr: address, min_uamounts: uint256[N_COINS]):
    use_lending: bool[N_COINS] = USE_LENDING
    tethered: bool[N_COINS] = TETHERED

    for i in range(N_COINS):
        if use_lending[i]:
            _coin: address = self.coins[i]
            ok: uint256 = cERC20(_coin).redeem(cERC20(_coin).balanceOf(self))
            if ok > 0:
                raise "Could not redeem coin"

        _ucoin: address = self.underlying_coins[i]
        _uamount: uint256 = ERC20(_ucoin).balanceOf(self)
        assert _uamount >= min_uamounts[i], "Not enough coins withdrawn"

        if tethered[i]:
            USDT(_ucoin).transfer(_addr, _uamount)
        else:
            assert_modifiable(ERC20(_ucoin).transfer(_addr, _uamount))


@public
@nonreentrant('lock')
def remove_liquidity(_amount: uint256, min_uamounts: uint256[N_COINS]):
    zeros: uint256[N_COINS] = ZEROS

    assert_modifiable(ERC20(self.token).transferFrom(msg.sender, self, _amount))
    Curve(self.curve).remove_liquidity(_amount, zeros)

    self._send_all(msg.sender, min_uamounts)


@public
@nonreentrant('lock')
def remove_liquidity_imbalance(uamounts: uint256[N_COINS], max_burn_amount: uint256):
    """
    Get max_burn_amount in, remove requested liquidity and transfer back what is left
    """
    use_lending: bool[N_COINS] = USE_LENDING
    tethered: bool[N_COINS] = TETHERED
    _token: address = self.token

    amounts: uint256[N_COINS] = uamounts
    for i in range(N_COINS):
        if use_lending[i]:
            rate: uint256 = cERC20(self.coins[i]).exchangeRateCurrent()
            amounts[i] = amounts[i] * rate / LENDING_PRECISION
        # if not use_lending - all good already

    # Transfrer max tokens in
    _tokens: uint256 = ERC20(_token).balanceOf(msg.sender)
    if _tokens > max_burn_amount:
        _tokens = max_burn_amount
    assert_modifiable(ERC20(_token).transferFrom(msg.sender, self, _tokens))

    Curve(self.curve).remove_liquidity_imbalance(amounts, max_burn_amount)

    # Transfer unused tokens back
    _tokens = ERC20(_token).balanceOf(self)
    assert_modifiable(ERC20(_token).transfer(msg.sender, _tokens))

    # Unwrap and transfer all the coins we've got
    self._send_all(msg.sender, ZEROS)
