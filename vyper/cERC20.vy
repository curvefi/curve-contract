# Interface for the used methods in Compound cERC20
#
# Events

Transfer: event({_from: address, _to: address, _value: uint256})
Approval: event({_owner: address, _spender: address, _value: uint256})

# Functions

@constant
@public
def totalSupply() -> uint256:
    pass

@constant
@public
def allowance(_owner: address, _spender: address) -> uint256:
    pass

@public
def transfer(_to: address, _value: uint256) -> bool:
    pass

@public
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    pass

@public
def approve(_spender: address, _value: uint256) -> bool:
    pass

@public
def burn(_value: uint256):
    pass

@public
def burnFrom(_to: address, _value: uint256):
    pass

@constant
@public
def name() -> string[64]:
    pass

@constant
@public
def symbol() -> string[32]:
    pass

@constant
@public
def decimals() -> uint256:
    pass

@constant
@public
def balanceOf(arg0: address) -> uint256:
    pass

@public
def mint(mintAmount: uint256) -> uint256:
    """
     @notice Sender supplies assets into the market and receives cTokens in exchange
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param mintAmount The amount of the underlying asset to supply
     @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
    """
    pass

@public
def redeem(redeemTokens: uint256) -> uint256:
    """
     @notice Sender redeems cTokens in exchange for the underlying asset
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param redeemTokens The number of cTokens to redeem into underlying
     @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
    """
    pass

@public
def redeemUnderlying(redeemAmount: uint256) -> uint256:
    """
     @notice Sender redeems cTokens in exchange for a specified amount of underlying asset
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param redeemAmount The amount of underlying to redeem
     @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
    """
    pass

@constant
@public
def exchangeRateStored() -> uint256:
    """
     @notice Calculates the exchange rate from the underlying to the CToken
     @dev This function does not accrue interest before calculating the exchange rate
     @return Calculated exchange rate scaled by 1e18
    """
    pass

@public
def exchangeRateCurrent() -> uint256:
    """
     * @notice Accrue interest then return the up-to-date exchange rate
     * @return Calculated exchange rate scaled by 1e18
    """
    pass

@public
@constant
def supplyRatePerBlock() -> uint256:
    pass

@public
@constant
def accrualBlockNumber() -> uint256:
    pass
