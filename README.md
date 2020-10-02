# curve-contract

Vyper contracts used in [Curve](https://www.curve.fi/) exchange pools.

## Overview

Curve is an exchange liquidity pool on Ethereum designed for extremely efficient stablecoin trading and low risk, supplemental fee income for liquidity providers, without an opportunity cost.

Curve allows users to trade between correlated cryptocurrencies with a bespoke low slippage, low fee algorithm. The liquidity pool is also supplied to lending protocol where it generates additional income for liquidity providers.

## Testing and Development

### Dependencies

* [python3](https://www.python.org/downloads/release/python-368/) version 3.6 or greater, python3-dev
* [brownie](https://github.com/iamdefinitelyahuman/brownie) - tested with version [1.11.6](https://github.com/eth-brownie/brownie/releases/tag/v1.11.6)
* [ganache-cli](https://github.com/trufflesuite/ganache-cli) - tested with version [6.11.0](https://github.com/trufflesuite/ganache-cli/releases/tag/v6.11.0)

Curve contracts are compiled using [Vyper](https://github.com/vyperlang/vyper), however installation of the required Vyper versions is handled by Brownie.

### Setup

To get started, first create and initialize a Python [virtual environment](https://docs.python.org/3/library/venv.html). Next, clone the repo and install the developer dependencies:

```bash
git clone https://github.com/curvefi/curve-contract.git
cd curve-contract
pip install -r requirements
```

### Organization and Workflow

* New Curve pools are built from the contract templates at [`contracts/pool-templates`](contracts/pool-templates)
* Once deployed, the contracts for a pool are added to [`contracts/pools`](contracts/pools)

See the documentation within [`contracts`](contracts) and it's subdirectories for more detailed information on how to get started developing on Curve.

### Running the Tests

The [test suite](tests) contains common tests for all Curve pools, as well as unique per-pool tests. To run the entire suite:

```bash
brownie test
```

To run tests on a specific pool:

```bash
pytest tests --pool <POOL NAME>
```

Valid pool names are the names of the subdirectories within [`contracts/pools`](contracts/pools). For templates, prepend `template-` to the subdirectory names within [`contracts/pool-templates`](../contracts/pool-templates). For example, the base template is `template-base`.

You can optionally include the `--coverage` flag to view a coverage report upon completion of the tests.

## Deployment

To deploy a new pool based on one of the templates:

1. In [`brownie_hooks.py`](brownie_hooks.py), set the number of coins and decimal places.
2. In [`scripts/deploy.py`](scripts/deploy.py), set the constructor parameters and deployer account.

To deploy a pool based on [`StableSwapBase`](contracts/pool-templates/StableSwapBase.vy) (without lending):

```bash
brownie run deploy base --network mainnet
```

To deploy a pool based on [`StableSwapYLend`](contracts/pool-templates/StableSwapYLend.vy) (with yearn-style lending):

```bash
brownie run deploy ylend --network mainnet
```

## Audits and Security

Curve smart contracts have been audited by Trail of Bits. These audit reports are made available on the [Curve website](https://www.curve.fi/audits).

There is also an active [bug bounty](https://www.curve.fi/bugbounty) for issues which can lead to substantial loss of money, critical bugs such as a broken live-ness condition, or irreversible loss of funds.

## License

(c) Curve.Fi, 2020 - [All rights reserved](LICENSE).
