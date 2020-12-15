# curve-contract/contracts/pools/obtc

[Curve oBTC metapool](https://www.curve.fi/obtc), allowing swaps via the Curve [sBTC pool](../sbtc).

## Contracts

* [`DepositOBTC`](DepositOBTC.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapOBTC`](StableSwapOBTC.vy): Curve stablecoin AMM contract

## Deployments

[`CurveContractV3`](../../tokens/CurveTokenV3.vy): [0x2fE94ea3d5d4a175184081439753DE15AeF9d614](https://etherscan.io/address/0x2fE94ea3d5d4a175184081439753DE15AeF9d614)
* [`DepositOBTC`](DepositOBTC.vy): [0xd5BCf53e2C81e1991570f33Fa881c49EEa570C8D](https://etherscan.io/address/0xd5BCf53e2C81e1991570f33Fa881c49EEa570C8D)
* [`LiquidityGaugeV2`](../../gauges/LiquidityGaugeV2.vy): [0x11137B10C210b579405c21A07489e28F3c040AB1](https://etherscan.io/address/0x11137B10C210b579405c21A07489e28F3c040AB1)
* [`StableSwapOBTC`](StableSwapOBTC.vy): [0xd81dA8D904b52208541Bade1bD6595D8a251F8dd](https://etherscan.io/address/0xd81dA8D904b52208541Bade1bD6595D8a251F8dd)

## Stablecoins

Curve oBTC metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between oBTC and the Curve sBTC LP token.

* `oBTC`: [0x8064d9Ae6cDf087b1bcd5BDf3531bD5d8C537a68](https://etherscan.io/address/0x8064d9Ae6cDf087b1bcd5BDf3531bD5d8C537a68)
* `sbtcCRV`: [0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3](https://etherscan.io/address/0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3)

## Base Pool coins

The sBTC LP token may be wrapped or unwrapped to provide swaps between oBTC and the following coins:

* `renBTC`: [0xeb4c2781e4eba804ce9a9803c67d0893436bb27d](https://etherscan.io/address/0xeb4c2781e4eba804ce9a9803c67d0893436bb27d)
* `wBTC`: [0x2260fac5e5542a773aa44fbcfedf7c193bc2c599](https://etherscan.io/address/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599)
* `sBTC`: [0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6](https://etherscan.io/address/0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6)
