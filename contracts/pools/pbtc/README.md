# curve-contract/contracts/pools/pbtc

[Curve pBTC metapool](https://www.curve.fi/pbtc), allowing swaps via the Curve [sBTC pool](../sbtc).

## Contracts

* [`DepositPBTC`](DepositPBTC.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapPBTC`](StableSwapPBTC.vy): Curve stablecoin AMM contract

## Deployments

[`CurveContractV2`](../../tokens/CurveTokenV2.vy): [0xDE5331AC4B3630f94853Ff322B66407e0D6331E8](https://etherscan.io/address/0xDE5331AC4B3630f94853Ff322B66407e0D6331E8)
* [`DepositPBTC`](DepositPBTC.vy): [0x11F419AdAbbFF8d595E7d5b223eee3863Bb3902C](https://etherscan.io/address/0x11F419AdAbbFF8d595E7d5b223eee3863Bb3902C)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0xd7d147c6Bb90A718c3De8C0568F9B560C79fa416](https://etherscan.io/address/0xd7d147c6Bb90A718c3De8C0568F9B560C79fa416)
* [`StableSwapPBTC`](StableSwapPBTC.vy): [0x7F55DDe206dbAD629C080068923b36fe9D6bDBeF](https://etherscan.io/address/0x7F55DDe206dbAD629C080068923b36fe9D6bDBeF)

## Stablecoins

Curve pBTC metapool utilizes the supports swaps between the following assets:

## Direct swaps

Direct swaps are possible between pBTC and the Curve sBTC LP token.

* `pBTC`: [0x5228a22e72ccC52d415EcFd199F99D0665E7733b](https://etherscan.io/address/0x5228a22e72ccC52d415EcFd199F99D0665E7733b)
* `sbtcCRV`: [0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3](https://etherscan.io/address/0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3)

## Base Pool coins

The sBTC LP token may be wrapped or unwrapped to provide swaps between pBTC and the following coins:

* `renBTC`: [0xeb4c2781e4eba804ce9a9803c67d0893436bb27d](https://etherscan.io/address/0xeb4c2781e4eba804ce9a9803c67d0893436bb27d)
* `wBTC`: [0x2260fac5e5542a773aa44fbcfedf7c193bc2c599](https://etherscan.io/address/0x2260fac5e5542a773aa44fbcfedf7c193bc2c599)
* `sBTC`: [0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6](https://etherscan.io/address/0xfe18be6b3bd88a2d2a7f928d00292e7a9963cfc6)
