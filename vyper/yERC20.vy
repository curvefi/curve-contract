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
def deposit(depositAmount: uint256):
    """
     @notice Sender supplies assets into the market and receives yTokens in exchange
     @dev Accrues interest whether or not the operation succeeds, unless reverted
     @param depositAmount The amount of the underlying asset to supply
    """
    pass

@public
def withdraw(withdrawTokens: uint256):
    """
     @notice Sender redeems yTokens in exchange for the underlying asset
     @param withdrawTokens The number of yTokens to redeem into underlying
    """
    pass

@constant
@public
def getPricePerFullShare() -> uint256:
    """
     @notice Calculates the amount of underlying to the yToken
     @return Calculated underlying scaled by 1e18
    """
    pass
