# curve-contract/contracts/pools/bbtc

[Curve bBTC metapool](https://www.curve.fi/bbtc), allowing swaps via the Curve [sBTC pool](../sbtc).

## Contracts

* [`DepositBBTC`](DepositBBTC.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapBBTC`](StableSwapBBTC.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV2`](../../tokens/CurveTokenV3.vy): [0x410e3E86ef427e30B9235497143881f717d93c2A](https://etherscan.io/address/0x410e3E86ef427e30B9235497143881f717d93c2A)
* [`DepositBBTC`](DepositBBTC.vy): [0xC45b2EEe6e09cA176Ca3bB5f7eEe7C47bF93c756](https://etherscan.io/address/0xC45b2EEe6e09cA176Ca3bB5f7eEe7C47bF93c756)
* [`LiquidityGaugeV2`](https://github.com/curvefi/curve-dao-contracts/blob/master/contracts/gauges/LiquidityGaugeV2.vy): [0xdFc7AdFa664b08767b735dE28f9E84cd30492aeE](https://etherscan.io/address/0xdFc7AdFa664b08767b735dE28f9E84cd30492aeE)
* [`StableSwapBBTC`](StableSwapBBTC.vy): [0x071c661B4DeefB59E2a3DdB20Db036821eeE8F4b](https://etherscan.io/address/0x071c661B4DeefB59E2a3DdB20Db036821eeE8F4b)

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
