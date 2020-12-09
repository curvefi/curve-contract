# curve-contract/contracts/pools/tbtc

[Curve tBTC metapool](https://www.curve.fi/tbtc), allowing swaps via the Curve [sBTC pool](../sbtc).

## Contracts

* [`DepositTBTC`](DepositTBTC.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapTBTC`](StableSwapTBTC.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0x64eda51d3Ad40D56b9dFc5554E06F94e1Dd786Fd](https://etherscan.io/address/0x64eda51d3Ad40D56b9dFc5554E06F94e1Dd786Fd)
* [`DepositTBTC`](DepositTBTC.vy): [0xaa82ca713D94bBA7A89CEAB55314F9EfFEdDc78c](https://etherscan.io/address/0xaa82ca713D94bBA7A89CEAB55314F9EfFEdDc78c)
* [`LiquidityGaugeReward`](../../gauges/LiquidityGaugeReward.vy): [0x6828bcF74279eE32f2723eC536c22c51Eed383C6](https://etherscan.io/address/0x6828bcF74279eE32f2723eC536c22c51Eed383C6)
* [`StableSwapTBTC`](StableSwapTBTC.vy): [0xC25099792E9349C7DD09759744ea681C7de2cb66](https://etherscan.io/address/0xC25099792E9349C7DD09759744ea681C7de2cb66)

## Stablecoins

Curve tBTC metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between tBTC and the Curve sBTC LP token.

* `tBTC`: [0x8dAEBADE922dF735c38C80C7eBD708Af50815fAa](https://etherscan.io/address/0x8dAEBADE922dF735c38C80C7eBD708Af50815fAa)
* `sbtcCRV`: [0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3](https://etherscan.io/address/0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3)

## Base Pool coins

The sBTC LP token may be wrapped or unwrapped to provide swaps between tBTC and the following coins:

* `renBTC`: [0xeb4c2781e4eba804ce9a9803c67d0893436bb27d](https://etherscan.io/address/0xeb4c2781e4eba804ce9a9803c67d0893436bb27d)
* `wBTC`: [0x2260fac5e5542a773aa44fbcfedf7c193bc2c599](https://etherscan.io/address/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599)
* `sBTC`: [0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6](https://etherscan.io/address/0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6)
