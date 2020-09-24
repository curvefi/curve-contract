# curve-contract/contracts/pools

Deployed Curve pool contracts.

## Subdirectories

Each subdirectory holds contracts and other files specific to a single Curve pool.

* [`3pool`](3pool): [Tri-pool](https://www.curve.fi/3pool)
* [`busd`](busd): [BUSD pool](https://www.curve.fi/busd), with lending on [yearn.finance](https://yearn.finance/)
* [`compound`](compound): [Compound pool](https://www.curve.fi/compound), with lending on [Compound](https://compound.finance/)
* [`hbtc`](hbtc): [hBTC pool](https://www.curve.fi/hbtc)
* [`pax`](pax): [PAX pool](https://www.curve.fi/pax), with lending on [yearn.finance](https://yearn.finance/)
* [`ren`](ren): [RenBTC pool](https://www.curve.fi/ren)
* [`sbtc`](sbtc): [sBTC pool](https://www.curve.fi/sbtc)
* [`snow`](snow): [Snow pool](https://www.curve.fi/snow), for swaps between [yVault](https://feel-the-yearn.app/vaults) tokens
* [`susd`](susd): [sUSD pool](https://www.curve.fi/susdv2)
* [`usdt`](usdt): [USDT pool](https://www.curve.fi/usdt), with lending on [Compound](https://compound.finance/)
* [`y`](y): [Y pool](https://www.curve.fi/y), with lending on [yearn.finance](https://yearn.finance/)

## Development

### Adding a New Pool

* Contracts for a new pool should be placed in their own subdirectory using the same name as is given on the website.
* The LP token contract does not need to be included, unless it deviates from the standard contracts within [`contracts/testing`](../testing)
* Each subdirectory must contain a `pooldata.json` file using the structure given below. This is required in order to initialize fixtures when running the [test suite](../../tests).

```js
{
    "lp_contract": "CurveTokenV1", // LP token contract to use with this pool, from `contracts/tokens`
    "wrapped_contract": "yERC20",  // mock wrapped coin contract to use, from `contracts/testing`
    "coins": [                     // each list item represents 1 swappable coin within the pool
        {
            "decimals": 18,         // number of decimal places for the underlying coin
            "tethered": false,      // does the token contract return `None` on a successful transfer/approve?
            "wrapped": true,        // is wrapping used for this coin?
            "wrapped_decimals": 18, // decimal places for the wrapped coin - can be omitted if wrapped == false
            "withdrawal_fee": 0     // optional fee when converting wrapped to underlying, expressed in bps
        },
    ]
}
```
