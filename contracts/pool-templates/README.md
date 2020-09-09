# curve-contract/contracts/pool-templates

Contract templates used as the basis for future pools.

## Contracts

* [`StableSwapBase`](StableSwapBase.vy): Minimal pool implementation optimized for no lending
* [`StableSwapYLend`](StableSwapYLend.vy): Pool implementation with yearn-style lending

## Development

### Working with Templates

Contracts in this subdirectory contain special triple-dunder variables which are modified according to the quantity and properties of each stablecoin in a pool.

* `___N_COINS___`: The number of coins within the pool
* `___PRECISION_MUL___`: Array of integers that coin balances are multiplied by in order to adjust their precision to 18 decimal places
* `___RATES___`: Array of integers indicating the relative value of `1e18` tokens for each stablecoin

These variables are substituted out at compile-time. To set the actual values you should modify [`brownie_hooks.py`](../../brownie_hooks.py) rather than changing them directly in the template.
