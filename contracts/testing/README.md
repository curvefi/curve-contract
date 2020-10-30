# curve-contract/contracts/testing

Contracts used exclusively for testing. These are not considered part of Curve and so do not fall under the Curve [license](../../LICENSE).

## Contracts

* [`cERC20`](cERC20.vy): Mintable ERC20 with mocked compound cToken lending functionality
* [`ERC20Mock`](ERC20.vy): Mintable ERC20 that returns `True` on successful calls
* [`ERC20MockNoReturn`](ERC20LP.vy): Mintable ERC20 that returns `None` on successful calls
* [`renERC20`](renERC20.vy): Mintable ERC20 with mocked renBTC functionality
* [`yERC20`](yERC20.vy): Mintable ERC20 with mocked yearn yToken lending functionality

## Development

### Minting test tokens

All test tokens implement the following method to allow minting to arbitrary addresses during testing:

```python
def _mint_for_testing(_target: address, _value: uint256) -> bool:
```

* `_target`: Address to mint tokens to
* `_value`: Number of tokens to mint

When called on a wrapped token, an amount of the underlying token is also minted at the wrapped token address in order to ensure unwrapping is possible.
