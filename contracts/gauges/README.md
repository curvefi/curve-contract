# curve-contract/contracts/gauges

Liquidity gauge contracts. These contracts are used to stake LP tokens and handle distribution of the CRV governance token.

These contract are a part of the [Curve DAO](https://github.com/curvefi/curve-dao-contracts). They are included here to simplify the deployment process for new pools.

Licensed under the [MIT license](https://github.com/curvefi/curve-dao-contracts/blob/master/LICENSE).

## Contracts

* [`LiquidityGauge`](LiquidityGauge.vy): Measures the amount of liquidity provided by each user
* [`LiquidityGaugeReward`](LiquidityGaugeReward.vy): Measures provided liquidity and stakes using [Synthetix rewards contract](https://github.com/Synthetixio/synthetix/blob/master/contracts/StakingRewards.sol)
