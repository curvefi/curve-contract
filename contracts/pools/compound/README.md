# curve-contract/contracts/pools/compound

[Curve Compound pool](https://www.curve.fi/compound), with lending on [Compound](https://compound.finance/).

## Contracts

* [`DepositCompound`](DepositCompound.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapCompound`](StableSwapCompound.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV1`](../../tokens/CurveTokenV1.vy): [0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2](https://etherscan.io/address/0x845838DF265Dcd2c412A1Dc9e959c7d08537f8a2)
* [`DepositCompound`](DepositCompound.vy): [0xeb21209ae4c2c9ff2a86aca31e123764a3b6bc06](https://etherscan.io/address/0xeb21209ae4c2c9ff2a86aca31e123764a3b6bc06)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0x7ca5b0a2910B33e9759DC7dDB0413949071D7575](https://etherscan.io/address/0x7ca5b0a2910b33e9759dc7ddb0413949071d7575)
* [`StableSwapCompound`](StableSwapCompound.vy): [0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56](https://etherscan.io/address/0xA2B47E3D5c44877cca798226B7B8118F9BFb7A56)

## Stablecoins

Curve Compound pool supports swaps between the following stablecoins:

### Wrapped

* `cDAI`: [0x5d3a536e4d6dbd6114cc1ead35777bab948e3643](https://etherscan.io/token/0x5d3a536e4d6dbd6114cc1ead35777bab948e3643)
* `cUSDC`: [0x39aa39c021dfbae8fac545936693ac917d5e7563](https://etherscan.io/token/0x39aa39c021dfbae8fac545936693ac917d5e7563)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
