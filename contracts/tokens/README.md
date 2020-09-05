# curve-contract/contracts/tokens

[ERC20](https://eips.ethereum.org/EIPS/eip-20) contracts used for pool liquidity provider tokens.

## Contracts

* [`CurveTokenV1`](CurveTokenV1.vy): LP token targetting Vyper [`^0.1.0-beta.16`](https://vyper.readthedocs.io/en/stable/release-notes.html#v0-1-0-beta-16)
* [`CurveTokenV2`](CurveTokenV2.vy): LP token targetting Vyper [`^0.2.0`](https://vyper.readthedocs.io/en/stable/release-notes.html#v0-2-1)

## Development

Token contracts should be referenced via an absolute import statement. Regardless of which contract is used it should be aliased as `CurveToken`. For example:

```python
from contracts.tokens import CurveTokenV2 as CurveToken
```
