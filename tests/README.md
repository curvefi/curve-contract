# curve-contract/tests

Test cases for Curve pools.

## Organization

* Tests are organized according to the specific pool, and then split between integration and unitary tests.
* Common tests for all pools are located in [`tests/common`](common).
* Valid pool names are the names of the subdirectories within [`contracts/pools`](../contracts/pools).

## Running the tests

To run the entire suite:

```bash
brownie test
```

To run tests on a specific pool:

```bash
pytest tests --pool <POOL NAME>
```

You can optionally include the `--coverage` flag to view a coverage report upon completion of the tests.

## Fixtures

[Fixtures](https://docs.pytest.org/en/stable/fixture.html) are [parametrized](https://docs.pytest.org/en/stable/parametrize.html) to work with every pool in [`contracts/pools`](../contracts/pools). To add a new pool to the test suite, create a `pooldata.json` in the same subdirectory. You can read about the structure of this JSON file [here](../contracts/pools/README.md).

Some commonly used fixtures:

### `swap`

A deployed [`StableSwap`](../contracts/pool-templates) contract for the pool being tested.

### `pool_token`

A deployed [`CurveToken`](../contracts/tokens) contract representing the LP token for the active pool.

### `wrapped_coins`

A list of deployed ERC20 contracts representing the lent-out coins in the active pool. If the pool does not support lending, these will be the same as the underlying contracts.

### `underlying_coins`

A list of deployed ERC20 contracts representing the underlying coins in the active pool.

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

### `itercoins(*arg)`
Parametrizes each of the given arguments with a range of numbers equal to the total number of coins for the given pool. When multiple arguments are given, each argument has a unique value for every generated test.

For example, `itercoins("send", "recv")` with a pool of 3 coins will parametrize with the sequence `[(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]`.

```python
@pytest.mark.itercoins("send", "recv"):
def test_swap(accounts, swap, send, recv):
    swap.exchange(send, recv, 0, 0, {'from': accounts[0]})
```
