# curve-contract/contracts/pools/bbtc

[Curve bBTC metapool](https://www.curve.fi/bbtc), allowing swaps via the Curve [sBTC pool](../sbtc).

## Contracts

* [`DepositBBTC`](DepositBBTC.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapBBTC`](StableSwapBBTC.vy): Curve stablecoin AMM contract

## Deployments

<!-- * [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [](https://etherscan.io/address/)
* [`DepositBBTC`](DepositBBTC.vy): [](https://etherscan.io/address/)
* [`LiquidityGaugeReward`](../../gauges/LiquidityGaugeReward.vy): [](https://etherscan.io/address/)
* [`StableSwapBBTC`](StableSwapBBTC.vy): [](https://etherscan.io/address/) -->

## Stablecoins

Curve bBTC metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between bBTC and the Curve sBTC LP token.

* `bBTC`: [0x9be89d2a4cd102d8fecc6bf9da793be995c22541](https://etherscan.io/address/0x9be89d2a4cd102d8fecc6bf9da793be995c22541)
* `sbtcCRV`: [0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3](https://etherscan.io/address/0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3)

## Base Pool coins

The sBTC LP token may be wrapped or unwrapped to provide swaps between bBTC and the following coins:

* `renBTC`: [0xeb4c2781e4eba804ce9a9803c67d0893436bb27d](https://etherscan.io/address/0xeb4c2781e4eba804ce9a9803c67d0893436bb27d)
* `wBTC`: [0x2260fac5e5542a773aa44fbcfedf7c193bc2c599](https://etherscan.io/address/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599)
* `sBTC`: [0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6](https://etherscan.io/address/0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6)
