# curve-contract/contracts

All contract sources are within this directory.

## Subdirectories

* [`gauges`](gauges): Liquidity gauge contracts, used to staked LP tokens and handle CRV distribution. Part of the [Curve DAO](https://github.com/curvefi/curve-dao-contracts), included here to simplify the deployment process for new pools.
* [`pool-templates`](pool-templates): Contract templates used as a base when constructing new pools.
* [`pools`](pools): Deployed Curve pool contracts.
* [`testing`](testing): Contracts used exclusively for testing. Not considered to be a core part of this project.
* [`tokens`](tokens): [ERC20](https://eips.ethereum.org/EIPS/eip-20) contracts used for pool liquidity provider tokens.
