# Interface for the used methods in Compound cERC20

@public
def mint(uint256 mintAmount) -> uint256:
    """
     @notice Sender supplies assets into the market and receives cTokens in exchange
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param mintAmount The amount of the underlying asset to supply
     @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
    """
    pass

@public
def redeem(uint256 redeemTokens) -> uint256:
    """
     @notice Sender redeems cTokens in exchange for the underlying asset
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param redeemTokens The number of cTokens to redeem into underlying
     @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
    """
    pass

@public
def redeemUnderlying(uint256 redeemAmount) -> uint256:
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
