# A "zap" to deposit/withdraw Curve contract without too many transactions
from vyper.interfaces import ERC20
import cERC20 as cERC20


# Tether transfer-only ABI
contract USDT:
    def transfer(_to: address, _value: uint256): modifying
    def transferFrom(_from: address, _to: address, _value: uint256): modifying


contract Curve:
    def add_liquidity(amounts: uint256[N_COINS], min_mint_amount: uint256): modifying
    def remove_liquidity(_amount: uint256, min_amounts: uint256[N_COINS]):
    modifying
    def remove_liquidity_imbalance(amounts: uint256[N_COINS], max_burn_amount: uint256): modifying


N_COINS: constant(int128) = ___N_COINS___
TETHERED: constant(bool[N_COINS]) = ___TETHERED___
USE_LENDING: constant(bool[N_COINS]) = ___USE_LENDING___
ZERO256: constant(uint256) = 0  # This hack is really bad XXX
ZEROS: constant(uint256[N_COINS]) = ___N_ZEROS___  # <- change

coins: public(address[N_COINS])
underlying_coins: public(address[N_COINS])
swap: public(address)
token: public(address)


@public
def __init__(_coins: address[N_COINS], _underlying_coins: address[N_COINS],
             _swap: address, _pool_token: address):
    self.coins = _coins
    self.underlying_coins = _underlying_coins
    self.swap = _swap
    self.token = _token


@public
@nonreentrant('lock')
def add_liquidity(uamounts: uint256[N_COINS], min_mint_amount: uint256):
    use_lending: bool[N_COINS] = USE_LENDING
    tethered: bool[N_COINS] = TETHERED
    amounts: uint256[N_COINS] = ZEROS

    for i in range(N_COINS):
        # Transfer the underlying coin from owner
        if tethered[i]:
            USDT(self.underlying_coins[i]).transferFrom(
                msg.sender, self, uamounts[i])
        else:
            assert_modifiable(ERC20(self.underlying_coins[i])\
                .transferFrom(msg.sender, self, uamounts[i]))

        # Mint if needed
        if use_lending[i]:
            ERC20(self.underlying_coins[i]).approve(self.coins[i], uamounts[i])
            ok = cERC20(self.coins[i]).mint(uamounts[i])
            if ok > 0:
                raise "Could not mint coin"
            amounts[i] = cERC20(self.coins[i]).balanceOf(self)
        else:
            amounts[i] = uamounts[i]

    Curve(self.swap).add_liquidity(amounts, min_mint_amount)

    tokens: uint256 = ERC20(self.token).balanceOf(self)
    assert_modifiable(ERC20(self.token).transfer(msg.sender, tokens))
