# curve-contract/contracts/pool-templates

Contract templates used as the basis for future pools.

## Subdirectories

Each subdirectory holds contracts and other files specific to a single Curve pool template.

* [`base`]: Minimal pool implementation optimized for no lending
* [`meta`]: Metapool implementation for swapping base assets against a Curve LP token
* [`y`]: Pool implementation with yearn-style lending

## Development

### Working with Templates

Contracts in this subdirectory contain special triple-dunder variables which are modified according to the quantity and properties of each stablecoin in a pool.

* `___USE_LENDING___`: Array of booleans indicating whether each underlying coin in the pool is lent on the associated lending protocol
* `___N_COINS___`: The number of coins within the pool
* `___PRECISION_MUL___`: Array of integers that coin balances are multiplied by in order to adjust their precision to 18 decimal places
* `___RATES___`: Array of integers indicating the relative value of `1e18` tokens for each stablecoin

Metapools also make use of the following variables:

* `___BASE_N_COINS___`: The number of coins within the base pool
* `___BASE_PRECISION_MUL___`: Array of integers that base coin balances are multiplied by to adjust their precision to 18 decimal places
* `___BASE_RATES___`: Array of integers indicating the relative walue of `1e18` tokens for each base pool stablecoin

These variables are substituted out at compile-time. To set the values, edit the `pooldata.json` file within the template directory.

The layout of a template's `pooldata.json` is similar to that of an actual pool, but less fields are required:

```js
{
    "wrapped_contract": "yERC20",   // mock wrapped coin contract to use, from `contracts/testing`
    "coins": [                      // each list item represents 1 swappable coin within the pool
        {
            "decimals": 18,          // number of decimal places for the underlying coin
            "tethered": false,       // does the token contract return `None` on a successful transfer/approve?
            "wrapped": true,         // is wrapping used for this coin?
            "wrapped_decimals": 18,  // decimal places for the wrapped coin - can be omitted if wrapped == false
        },
    ]
}
```

