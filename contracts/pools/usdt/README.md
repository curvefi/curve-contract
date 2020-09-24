# curve-contract/contracts/pools/usdt

[Curve USDT pool](https://www.curve.fi/usdt), with lending on [Compound](https://compound.finance/).

**NOTE**: This pool was deprecated. It has very little liquidity and trade volumes.

## Contracts

* [`DepositUSDT`](DepositUSDT.vy): Depositor contract, used to wrap underlying tokens prior to depositing them into the pool
* [`StableSwapUSDT`](StableSwapUSDT.vy): Curve stablecoin AMM contract

## Deployments

* [`CurveContractV1`](../../tokens/CurveTokenV1.vy): [0x9fC689CCaDa600B6DF723D9E47D84d76664a1F23](https://etherscan.io/address/0x9fC689CCaDa600B6DF723D9E47D84d76664a1F23)
* [`DepositUSDT`](DepositUSDT.vy): [0xac795d2c97e60df6a99ff1c814727302fd747a80](https://etherscan.io/address/0xac795d2c97e60df6a99ff1c814727302fd747a80)
* [`LiquidityGauge`](../../gauges/LiquidityGauge.vy): [0xBC89cd85491d81C6AD2954E6d0362Ee29fCa8F53](https://etherscan.io/address/0xbc89cd85491d81c6ad2954e6d0362ee29fca8f53)
* [`StableSwapUSDT`](StableSwapUSDT.vy): [0x52EA46506B9CC5Ef470C5bf89f17Dc28bB35D85C](https://etherscan.io/address/0x52EA46506B9CC5Ef470C5bf89f17Dc28bB35D85C)

## Stablecoins

Curve USDT pool supports swaps between the following stablecoins:

### Wrapped

* `cDAI`: [0x5d3a536e4d6dbd6114cc1ead35777bab948e3643](https://etherscan.io/token/0x5d3a536e4d6dbd6114cc1ead35777bab948e3643)
* `cUSDC`: [0x39aa39c021dfbae8fac545936693ac917d5e7563](https://etherscan.io/token/0x39aa39c021dfbae8fac545936693ac917d5e7563)

### Underlying

* `DAI`: [0x6b175474e89094c44da98b954eedeac495271d0f](https://etherscan.io/token/0x6b175474e89094c44da98b954eedeac495271d0f)
* `USDC`: [0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48](https://etherscan.io/token/0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48)
* `USDT`: [0xdac17f958d2ee523a2206206994597c13d831ec7](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7)
