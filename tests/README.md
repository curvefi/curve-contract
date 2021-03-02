# curve-contract/tests

Test cases for Curve pools.

## Subdirectories

- [`forked`](forked): Tests designed for use in a forked mainnet
- [`fixtures`](fixtures): [Pytest fixtures](https://docs.pytest.org/en/latest/fixture.html)
- [`pools`](pools): Tests for [pool](../contracts/pools) contracts
- [`token`](token): Tests for [LP token](../contracts/tokens) contracts
- [`zaps`](zaps): Tests for deposit contracts

## Files

- [`conftest.py`](conftest.py): Base configuration file for the test suite.
- [`simulation.py`](simulation.py): A python model of the math used within Curve's contracts. Used for testing expected outcomes with actual results.

## Organization

- Tests are organized by general category, then split between unitary and integration tests.
- Common tests for all pools are located in [`tests/pools/common`](pools/common), for zaps in [`tests/zaps/common`](zaps/common).
- Common metapool tests are located at [`tests/pools/meta`](pools/meta), for zaps in [`tests/zaps/meta`](zaps/meta).
- Valid pool names are the names of the subdirectories within [`contracts/pools`](../contracts/pools).
- For pool templates, prepend `template-` to the subdirectory names within [`contracts/pool-templates`](../contracts/pool-templates). For example, the base template is `template-base`.

## Running the tests

To run the entire suite:

```bash
brownie test
```

Note that this executes over 10,000 tests and may take a significant amount of time to finish.

### Test Collection Filters

The test suite is divided into several logical categories. Tests may be filtered using one or more flags:

- `--pool <POOL NAME>`: only run tests against a specific pool
- `--integration`: only run integration tests (tests within an `integration/` subdirectory)
- `--unitary`: only run unit tests (tests NOT found in an `integration/` subdirectory)

For example, to only run the unit tests for 3pool:

```bash
brownie test --pool 3pool --unitary
```

## Testing against a forked mainnet

To run the test suite against a forked mainnet:

```bash
brownie test --network mainnet-fork
```

In this mode, the actual underlying and wrapped coins are used for testing. Note that forked mode can be _very slow_, especially if you are running against a public node.

## Fixtures

Test fixtures are located within the [`tests/fixtures`](fixtures) subdirectory. New fixtures should be added here instead of within the base [`conftest.py`](conftest.py).

All fixtures are [documented](fixtures/README.md) within the fixtures subdirectory readme.

## Markers

We use the following custom [markers](https://docs.pytest.org/en/stable/example/markers.html) to parametrize common tests across different pools:

### `skip_pool(*pools)`

Exclude one or more pools from the given test.

```python
@pytest.mark.skip_pool("compound", "usdt", "y")
def test_only_some_pools(swap):
    ...
```

### `target_pool(*pools)`

Only run the given test against one or more pools specified in the marker.

```python
@pytest.mark.target_pool("ren", "sbtc")
def test_btc_pools(swap):
    ...
```

### `skip_pool_type(*pool_types)`

Exclude specific pool types from the given test.

```python
@pytest.mark.skip_pool_type("meta", "eth")
def test_not_metapools(swap):
    ...
```

The available pool types are: `arate`, `crate`, `eth`, `meta`.
By default, the pool type is `base`.

### `lending`

Only run the given test against pools that involve lending.

```python
@pytest.mark.lending
def test_underlying(swap):
    ...
```

### `zap`

Only run the given test against pools that use a deposit contract.

```python
@pytest.mark.zap
def test_deposits(zap):
    ...
```

### `itercoins(*arg, underlying=False)`

Parametrizes each of the given arguments with a range of numbers equal to the total number of coins for the given pool. When multiple arguments are given, each argument has a unique value for every generated test.

For example, `itercoins("send", "recv")` with a pool of 3 coins will parametrize with the sequence `[(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]`.

If `underlying` is set as `True`, the upper bound of iteration corresponds to the true number of underlying coins. This is useful when testing metapools.

```python
@pytest.mark.itercoins("send", "recv"):
def test_swap(accounts, swap, send, recv):
    swap.exchange(send, recv, 0, 0, {'from': accounts[0]})
```
