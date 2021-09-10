# curve-contract/contracts/pools/tbtc2

[Curve tBTCv2 metapool](https://www.curve.fi/tbtc2), allowing swaps via the Curve [sBTC pool](../sbtc).

## Contracts

* [`DepositTBTC2`](DepositTBTC2.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapTBTC2`](StableSwapTBTC2.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveTokenV3`](../../tokens/CurveTokenV3.vy): [0xB6881e8b21a3cd6D23c4F90724E26e35BB8980bE](https://etherscan.io/address/0xB6881e8b21a3cd6D23c4F90724E26e35BB8980bE)
* [`DepositTBTC2`](DepositTBTC2.vy): [0x3264834ADA73a8b0B132ee52Fd5a367CF60E86C6](https://etherscan.io/address/0x3264834ADA73a8b0B132ee52Fd5a367CF60E86C6)
* [`LiquidityGaugeV3`](../../gauges/LiquidityGaugeV3.vy): [0xF816CFE922E03C2347664a4a61CAec409fcFF738](https://etherscan.io/address/0xF816CFE922E03C2347664a4a61CAec409fcFF738)
* [`StableSwapTBTC2`](StableSwapTBTC2.vy): [0x9e56512566236b8872b5798C8CB3a2b1a572A16C](https://etherscan.io/address/0x9e56512566236b8872b5798C8CB3a2b1a572A16C)

## Stablecoins

Curve tBTCv2 metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between tBTCv2 and the Curve sBTC LP token.

* `tBTCv2`: [0x18084fbA666a33d37592fA2633fD49a74DD93a88](https://etherscan.io/address/0x18084fbA666a33d37592fA2633fD49a74DD93a88)
* `sbtcCRV`: [0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3](https://etherscan.io/address/0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3)

## Base Pool coins

The sBTC LP token may be wrapped or unwrapped to provide swaps between tBTCv2 and the following coins:

* `renBTC`: [0xeb4c2781e4eba804ce9a9803c67d0893436bb27d](https://etherscan.io/address/0xeb4c2781e4eba804ce9a9803c67d0893436bb27d)
* `wBTC`: [0x2260fac5e5542a773aa44fbcfedf7c193bc2c599](https://etherscan.io/address/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599)
* `sBTC`: [0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6](https://etherscan.io/address/0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6)
