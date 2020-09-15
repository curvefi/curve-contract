# @version ^0.2.0

MAX_COINS: constant(int128) = 8
CALC_INPUT_SIZE: constant(int128) = 100


struct PoolArray:
    location: uint256
    decimals: bytes32
    underlying_decimals: bytes32
    rate_method_id: bytes32
    lp_token: address
    coins: address[MAX_COINS]
    ul_coins: address[MAX_COINS]
    calculator: address
    has_initial_A: bool
    is_v1: bool

struct PoolCoins:
    coins: address[MAX_COINS]
    underlying_coins: address[MAX_COINS]
    decimals: uint256[MAX_COINS]
    underlying_decimals: uint256[MAX_COINS]

struct PoolInfo:
    balances: uint256[MAX_COINS]
    underlying_balances: uint256[MAX_COINS]
    decimals: uint256[MAX_COINS]
    underlying_decimals: uint256[MAX_COINS]
    lp_token: address
    A: uint256
    future_A: uint256
    fee: uint256
    future_fee: uint256
    future_admin_fee: uint256
    future_owner: address
    initial_A: uint256
    initial_A_time: uint256
    future_A_time: uint256

struct PoolGauges:
    liquidity_gauges: address[10]
    gauge_types: int128[10]

struct CoinInfo:
    n_coins: int128
    balances: uint256[MAX_COINS]
    amp: uint256
    fee: uint256
    rates: uint256[MAX_COINS]
    precisions: uint256[MAX_COINS]
    is_underlying: bool
    i: int128
    j: int128

struct CoinList:
    coins: address[MAX_COINS]
    ucoins: address[MAX_COINS]


interface ERC20:
    def decimals() -> uint256: view
    def balanceOf(addr: address) -> uint256: view
    def approve(spender: address, amount: uint256) -> bool: nonpayable
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(spender: address, to: address, amount: uint256) -> bool: nonpayable

interface CurvePool:
    def A() -> uint256: view
    def future_A() -> uint256: view
    def fee() -> uint256: view
    def future_fee() -> uint256: view
    def future_admin_fee() -> uint256: view
    def future_owner() -> address: view
    def initial_A() -> uint256: view
    def initial_A_time() -> uint256: view
    def future_A_time() -> uint256: view
    def coins(i: uint256) -> address: view
    def underlying_coins(i: uint256) -> address: view
    def balances(i: uint256) -> uint256: view
    def get_dy(i: int128, j: int128, dx: uint256) -> uint256: view
    def get_dy_underlying(i: int128, j: int128, dx: uint256) -> uint256: view
    def exchange(i: int128, j: int128, dx: uint256, min_dy: uint256): payable
    def exchange_underlying(i: int128, j: int128, dx: uint256, min_dy: uint256): payable

interface CurvePoolV1:
    def coins(i: int128) -> address: view
    def underlying_coins(i: int128) -> address: view
    def balances(i: int128) -> uint256: view

interface GasEstimator:
    def estimate_gas_used(_pool: address, _from: address, _to: address) -> uint256: view

interface Calculator:
    def get_dx(n_coins: int128, balances: uint256[MAX_COINS], amp: uint256, fee: uint256,
               rates: uint256[MAX_COINS], precisions: uint256[MAX_COINS], underlying: bool,
               i: int128, j: int128, dx: uint256) -> uint256: view
    def get_dy(n_coins: int128, balances: uint256[MAX_COINS], amp: uint256, fee: uint256,
               rates: uint256[MAX_COINS], precisions: uint256[MAX_COINS], underlying: bool,
               i: int128, j: int128, dx: uint256[CALC_INPUT_SIZE]) -> uint256[CALC_INPUT_SIZE]: view

interface LiquidityGauge:
    def lp_token() -> address: view

interface GaugeController:
    def gauge_types(gauge: address) -> int128: view

event CommitNewAdmin:
    deadline: indexed(uint256)
    admin: indexed(address)

event NewAdmin:
    admin: indexed(address)

event TokenExchange:
    buyer: indexed(address)
    pool: indexed(address)
    token_sold: address
    token_bought: address
    amount_sold: uint256
    amount_bought: uint256

event PoolAdded:
    pool: indexed(address)
    rate_method_id: Bytes[4]

event PoolRemoved:
    pool: indexed(address)


admin: public(address)
transfer_ownership_deadline: uint256
future_admin: address

gauge_controller: address
pool_list: public(address[65536])   # master list of pools
pool_count: public(uint256)         # actual length of pool_list

pool_data: HashMap[address, PoolArray]

# mapping of estimated gas costs for pools and coins
# for a pool the values are [wrapped exchange, underlying exchange]
# for a coin the values are [transfer cost, 0]
gas_estimate_values: HashMap[address, uint256[2]]

# pool -> gas estimation contract
# used when gas costs for a pool are too complex to be handled by summing
# values in `gas_estimate_values`
gas_estimate_contracts: HashMap[address, address]

# mapping of coin -> coin -> pools for trading
# all addresses are converted to uint256 prior to storage. coin addresses are stored
# using the smaller value first. within each pool address array, the first value
# is shifted 16 bits to the left, and these 16 bits are used to store the array length.

markets: HashMap[uint256, HashMap[uint256, uint256[65536]]]
liquidity_gauges: HashMap[address, address[10]]

@external
def __init__(_gauge_controller: address):
    """
    @notice Constructor function
    """
    self.admin = msg.sender
    self.gauge_controller = _gauge_controller


@external
@payable
def __default__():
    pass


@external
@view
def find_pool_for_coins(_from: address, _to: address, i: uint256 = 0) -> address:
    """
    @notice Find an available pool for exchanging two coins
    @dev For coins where there is no underlying coin, or where
         the underlying coin cannot be swapped, the rate is
         given as 1e18
    @param _from Address of coin to be sent
    @param _to Address of coin to be received
    @param i Index value. When multiple pools are available
            this value is used to return the n'th address.
    @return Pool address
    """

    _first: uint256 = min(convert(_from, uint256), convert(_to, uint256))
    _second: uint256 = max(convert(_from, uint256), convert(_to, uint256))

    _addr: uint256 = self.markets[_first][_second][i]
    if i == 0:
        _addr = shift(_addr, -16)
    return convert(convert(_addr, bytes32), address)


@external
@view
def get_pool_coins(_pool: address) -> PoolCoins:
    """
    @notice Get information on coins in a pool
    @dev Empty values in the returned arrays may be ignored
    @param _pool Pool address
    @return Coin addresses, underlying coin addresses, underlying coin decimals
    """
    _coins: PoolCoins = empty(PoolCoins)
    _decimals_packed: bytes32 = self.pool_data[_pool].decimals
    _udecimals_packed: bytes32 = self.pool_data[_pool].underlying_decimals

    for i in range(MAX_COINS):
        ui: uint256 = convert(i, uint256)
        _coins.coins[i] = self.pool_data[_pool].coins[i]
        if _coins.coins[i] == ZERO_ADDRESS:
            break
        _coins.underlying_coins[i] = self.pool_data[_pool].ul_coins[i]
        _coins.decimals[i] = convert(slice(_decimals_packed, ui, 1), uint256)
        _coins.underlying_decimals[i] = convert(slice(_udecimals_packed, ui, 1), uint256)

    return _coins


@view
@internal
def _get_rates(_pool: address) -> uint256[MAX_COINS]:
    _rates: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    _rate_method_id: Bytes[4] = slice(self.pool_data[_pool].rate_method_id, 0, 4)

    for i in range(MAX_COINS):
        _coin: address = self.pool_data[_pool].coins[i]
        if _coin == ZERO_ADDRESS:
            break
        if _coin == self.pool_data[_pool].ul_coins[i]:
            _rates[i] = 10 ** 18
        else:
            _rates[i] = convert(
                raw_call(_coin, _rate_method_id, max_outsize=32, is_static_call=True), # dev: bad response
                uint256
            )

    return _rates


@external
@view
def get_pool_info(_pool: address) -> PoolInfo:
    """
    @notice Get information on a pool
    @dev Reverts if the pool address is unknown
    @param _pool Pool address
    @return balances, underlying balances, decimals, underlying decimals,
            lp token, liquidity gauge, amplification coefficient, fees
    """
    _pool_info: PoolInfo = empty(PoolInfo)

    _pool_info.lp_token = self.pool_data[_pool].lp_token
    _pool_info.A = CurvePool(_pool).A()
    _pool_info.future_A = CurvePool(_pool).future_A()
    _pool_info.fee = CurvePool(_pool).fee()
    _pool_info.future_fee = CurvePool(_pool).future_fee()
    _pool_info.future_admin_fee = CurvePool(_pool).future_admin_fee()
    _pool_info.future_owner = CurvePool(_pool).future_owner()

    if self.pool_data[_pool].has_initial_A:
        _pool_info.initial_A = CurvePool(_pool).initial_A()
        _pool_info.initial_A_time = CurvePool(_pool).initial_A_time()
        _pool_info.future_A_time = CurvePool(_pool).future_A_time()

    #_rate_method_id: Bytes[4] = slice(self.pool_data[_pool].rate_method_id, 0, 4)
    _rates: uint256[MAX_COINS] = self._get_rates(_pool)
    _decimals_packed: bytes32 = self.pool_data[_pool].decimals
    _udecimals_packed: bytes32 = self.pool_data[_pool].underlying_decimals
    _is_v1: bool = self.pool_data[_pool].is_v1

    for i in range(MAX_COINS):
        _coin: address = self.pool_data[_pool].coins[i]
        if _coin == ZERO_ADDRESS:
            assert i != 0
            break

        ui: uint256 = convert(i, uint256)
        _pool_info.decimals[i] = convert(slice(_decimals_packed, ui, 1), uint256)
        _pool_info.underlying_decimals[i] = convert(slice(_udecimals_packed, ui, 1), uint256)

        if _is_v1:
            _pool_info.balances[i] = CurvePoolV1(_pool).balances(i)
        else:
            _pool_info.balances[i] = CurvePool(_pool).balances(ui)

        _underlying_coin: address = self.pool_data[_pool].ul_coins[i]
        if _coin == _underlying_coin:
            _pool_info.underlying_balances[i] = _pool_info.balances[i]
        elif _underlying_coin != ZERO_ADDRESS:
            _pool_info.underlying_balances[i] = _pool_info.balances[i] * _rates[i] / 10 ** 18

    return _pool_info


@external
@view
def get_pool_rates(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get rates between coins and underlying coins
    @dev For coins where there is no underlying coin, or where
         the underlying coin cannot be swapped, the rate is
         given as 1e18
    @param _pool Pool address
    @return Rates between coins and underlying coins
    """
    return self._get_rates(_pool)


@view
@external
def get_pool_gauges(_pool: address) -> PoolGauges:
    """
    @notice Get a list of LiquidityGauge contracts associated with a pool
    @param _pool Pool address
    @return address[10] of gauge addresses, int128[10] of gauge types
    """
    _gauge_info: PoolGauges = empty(PoolGauges)
    _gauge_controller: address = self.gauge_controller
    for i in range(10):
        _gauge: address = self.liquidity_gauges[_pool][i]
        if _gauge == ZERO_ADDRESS:
            break
        _gauge_info.liquidity_gauges[i] = _gauge
        _gauge_info.gauge_types[i] = GaugeController(_gauge_controller).gauge_types(_gauge)

    return _gauge_info


@internal
@view
def _get_token_indices(
    _pool: address,
    _from: address,
    _to: address
) -> (int128, int128, bool):
    """
    Convert coin addresses to indices for use with pool methods.
    """
    i: int128 = -1
    j: int128 = i
    _coin: address = ZERO_ADDRESS
    _check_underlying: bool = True

    # check coin markets
    for x in range(MAX_COINS):
        _coin = self.pool_data[_pool].coins[x]
        if _coin == _from:
            i = x
        elif _coin == _to:
            j = x
        elif _coin == ZERO_ADDRESS:
            break
        else:
            continue
        if i >= 0 and j >= 0:
            return i, j, False
        if _coin != self.pool_data[_pool].ul_coins[x]:
            _check_underlying = False

    assert _check_underlying, "No available market"

    # check underlying coin markets
    for x in range(MAX_COINS):
        _coin = self.pool_data[_pool].ul_coins[x]
        if _coin == _from:
            i = x
        elif _coin == _to:
            j = x
        elif _coin == ZERO_ADDRESS:
            break
        else:
            continue
        if i >= 0 and j >= 0:
            return i, j, True

    raise "No available market"


@external
@view
def estimate_gas_used(_pool: address, _from: address, _to: address) -> uint256:
    """
    @notice Estimate the gas used in an exchange.
    @param _pool Pool address
    @param _from Address of coin to be sent
    @param _to Address of coin to be received
    @return Upper-bound gas estimate, in wei
    """
    _estimator: address = self.gas_estimate_contracts[_pool]
    if _estimator != ZERO_ADDRESS:
        return GasEstimator(_estimator).estimate_gas_used(_pool, _from, _to)

    # here we call `_get_token_indices` to find out if the exchange involves
    # wrapped or underlying coins, and convert the result to an integer that we
    # use as an index for `gas_estimate_values`
    # 0 == wrapped   1 == underlying
    _idx_underlying: uint256 = convert(self._get_token_indices(_pool, _from, _to)[2], uint256)

    _total: uint256 = self.gas_estimate_values[_pool][_idx_underlying]
    assert _total != 0  # dev: pool value not set

    for _addr in [_from, _to]:
        _gas: uint256 = self.gas_estimate_values[_addr][0]
        assert _gas != 0  # dev: coin value not set
        _total += _gas

    return _total


@external
@view
def get_exchange_amount(
    _pool: address,
    _from: address,
    _to: address,
    _amount: uint256
) -> uint256:
    """
    @notice Get the current number of coins received in an exchange
    @param _pool Pool address
    @param _from Address of coin to be sent
    @param _to Address of coin to be received
    @param _amount Quantity of `_from` to be sent
    @return Quantity of `_to` to be received
    """
    i: int128 = 0
    j: int128 = 0
    _is_underlying: bool = False
    i, j, _is_underlying = self._get_token_indices(_pool, _from, _to)

    if _is_underlying:
        return CurvePool(_pool).get_dy_underlying(i, j, _amount)

    return CurvePool(_pool).get_dy(i, j, _amount)


@external
@payable
@nonreentrant("lock")
def exchange(
    _pool: address,
    _from: address,
    _to: address,
    _amount: uint256,
    _expected: uint256
) -> bool:
    """
    @notice Perform an exchange.
    @dev Prior to calling this function you must approve
         this contract to transfer `_amount` coins from `_from`
    @param _from Address of coin being sent
    @param _to Address of coin being received
    @param _amount Quantity of `_from` being sent
    @param _expected Minimum quantity of `_from` received
           in order for the transaction to succeed
    @return True
    """
    i: int128 = 0
    j: int128 = 0
    _is_underlying: bool = False
    i, j, _is_underlying = self._get_token_indices(_pool, _from, _to)

    # record initial balance
    _initial_balance: uint256 = 0
    if _to == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        _initial_balance = self.balance - msg.value
    else:
        _initial_balance = ERC20(_to).balanceOf(self)

    # perform / verify input transfer
    if _from == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        assert _amount == msg.value, "Incorrect ETH amount"
    else:
        _response: Bytes[32] = raw_call(
            _from,
            concat(
                method_id("transferFrom(address,address,uint256)"),
                convert(msg.sender, bytes32),
                convert(self, bytes32),
                convert(_amount, bytes32),
            ),
            max_outsize=32,
        )
        if len(_response) != 0:
            assert convert(_response, bool)

    # perform coin exchange
    if _is_underlying:
        CurvePool(_pool).exchange_underlying(i, j, _amount, _expected, value=msg.value)
    else:
        CurvePool(_pool).exchange(i, j, _amount, _expected, value=msg.value)

    # perform output transfer
    _received: uint256 = 0
    if _to == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        _received = self.balance - _initial_balance
        send(msg.sender, _received)
    else:
        _received = ERC20(_to).balanceOf(self) - _initial_balance
        _response: Bytes[32] = raw_call(
            _to,
            concat(
                method_id("transfer(address,uint256)"),
                convert(msg.sender, bytes32),
                convert(_received, bytes32),
            ),
            max_outsize=32,
        )
        if len(_response) != 0:
            assert convert(_response, bool)

    log TokenExchange(msg.sender, _pool, _from, _to, _amount, _received)

    return True


@internal
def _get_coin_info(_pool: address, _from: address, _to: address) -> CoinInfo:
    _coin_info: CoinInfo = empty(CoinInfo)
    _coin_info.i, _coin_info.j, _coin_info.is_underlying = self._get_token_indices(_pool, _from, _to)

    _coin_info.amp = CurvePool(_pool).A()
    _coin_info.fee = CurvePool(_pool).fee()

    _decimals_packed: bytes32 = EMPTY_BYTES32
    if _coin_info.is_underlying:
        _decimals_packed = self.pool_data[_pool].underlying_decimals
    else:
        _decimals_packed = self.pool_data[_pool].decimals

    _coin: address = ZERO_ADDRESS
    _is_v1: bool = self.pool_data[_pool].is_v1
    _coin_info.rates = self._get_rates(_pool)

    for x in range(MAX_COINS):
        _coin = self.pool_data[_pool].coins[x]

        if _coin == ZERO_ADDRESS:
            _coin_info.n_coins = x
            break

        ux: uint256 = convert(x, uint256)
        if _is_v1:
            _coin_info.balances[x] = CurvePoolV1(_pool).balances(x)
        else:
            _coin_info.balances[x] = CurvePool(_pool).balances(ux)

        _decimals: uint256 = convert(slice(_decimals_packed, ux, 1), uint256)
        _coin_info.precisions[x] = 10 ** (18 - _decimals)

    return _coin_info


@external
def get_input_amount(_pool: address, _from: address, _to: address, _amount: uint256) -> uint256:
    """
    @notice Get the current number of coins required to receive the given amount in an exchange
    @param _pool Pool address
    @param _from Address of coin to be sent
    @param _to Address of coin to be received
    @param _amount Quantity of `_to` to be received
    @return Quantity of `_from` to be sent
    """
    _coin_info: CoinInfo = self._get_coin_info(_pool, _from, _to)

    return Calculator(self.pool_data[_pool].calculator).get_dx(
        _coin_info.n_coins,
        _coin_info.balances,
        _coin_info.amp,
        _coin_info.fee,
        _coin_info.rates,
        _coin_info.precisions,
        _coin_info.is_underlying,
        _coin_info.i,
        _coin_info.j,
        _amount,
    )


@external
def get_exchange_amounts(
    _pool: address,
    _from: address,
    _to: address,
    _amounts: uint256[CALC_INPUT_SIZE]
) -> uint256[CALC_INPUT_SIZE]:
    """
    @notice Get the current number of coins received in exchanges of varying amounts
    @param _pool Pool address
    @param _from Address of coin to be sent
    @param _to Address of coin to be received
    @param _amounts Array of quantities of `_from` to be sent
    @return Array of quantities of `_to` to be received
    """
    _coin_info: CoinInfo = self._get_coin_info(_pool, _from, _to)

    return Calculator(self.pool_data[_pool].calculator).get_dy(
        _coin_info.n_coins,
        _coin_info.balances,
        _coin_info.amp,
        _coin_info.fee,
        _coin_info.rates,
        _coin_info.precisions,
        _coin_info.is_underlying,
        _coin_info.i,
        _coin_info.j,
        _amounts,
    )


# Admin functions

@internal
def _add_pool(
    _pool: address,
    _n_coins: int128,
    _lp_token: address,
    _calculator: address,
    _rate_method_id: bytes32,
    _coins: address[MAX_COINS],
    _ucoins: address[MAX_COINS],
    _decimals: bytes32,
    _udecimals: bytes32,
    _has_initial_A: bool,
    _is_v1: bool,
):
    # add pool to pool_list
    _length: uint256 = self.pool_count
    self.pool_list[_length] = _pool
    self.pool_count = _length + 1
    self.pool_data[_pool].location = _length
    self.pool_data[_pool].lp_token = _lp_token
    self.pool_data[_pool].calculator = _calculator
    self.pool_data[_pool].rate_method_id = _rate_method_id
    self.pool_data[_pool].has_initial_A = _has_initial_A
    self.pool_data[_pool].is_v1 = _is_v1

    _decimals_packed: uint256 = 0
    _udecimals_packed: uint256 = 0

    _offset: int128 = 256
    for i in range(MAX_COINS):
        if i == _n_coins:
            break

        ui: uint256 = convert(i, uint256)
        _coin: address = _coins[i]
        _ul_coin: address = _ucoins[i]
        _offset -= 8

        # add decimals
        _value: uint256 = convert(slice(_decimals, ui, 1), uint256)
        if _value == 0:
            if _coin == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
                _value = 18
            else:
                _value = ERC20(_coin).decimals()
                assert _value < 256  # dev: decimal overflow

        _decimals_packed += shift(_value, _offset)

        if _ul_coin != ZERO_ADDRESS:
            _value = convert(slice(_udecimals, ui, 1), uint256)
            if _value == 0:
                if _ul_coin == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
                    _value = 18
                else:
                    _value = ERC20(_ul_coin).decimals()
                    assert _value < 256  # dev: decimal overflow

            _udecimals_packed += shift(_value, _offset)

        # add pool to markets
        for x in range(i, i + MAX_COINS):
            if x == i:
                continue
            if x == _n_coins:
                break

            _first: uint256 = min(convert(_coin, uint256), convert(_coins[x], uint256))
            _second: uint256 = max(convert(_coin, uint256), convert(_coins[x], uint256))

            _pool_zero: uint256 = self.markets[_first][_second][0]
            _length = _pool_zero % 65536
            if _pool_zero != 0:
                self.markets[_first][_second][_length] = convert(_pool, uint256)
                self.markets[_first][_second][0] = _pool_zero + 1
            else:
                self.markets[_first][_second][0] = shift(convert(_pool, uint256), 16) + 1

            if _ul_coin == ZERO_ADDRESS:
                continue
            if _ucoins[x] == ZERO_ADDRESS:
                continue
            if _ul_coin == _coin and _ucoins[x] == _coins[x]:
                continue

            _first = min(convert(_ul_coin, uint256), convert(_ucoins[x], uint256))
            _second = max(convert(_ul_coin, uint256), convert(_ucoins[x], uint256))

            _pool_zero = self.markets[_first][_second][0]
            _length = _pool_zero % 65536

            if _pool_zero != 0:
                self.markets[_first][_second][_length] = convert(_pool, uint256)
                self.markets[_first][_second][0] = _pool_zero + 1
            else:
                self.markets[_first][_second][0] = shift(convert(_pool, uint256), 16) + 1

    self.pool_data[_pool].decimals = convert(_decimals_packed, bytes32)
    self.pool_data[_pool].underlying_decimals = convert(_udecimals_packed, bytes32)

    log PoolAdded(_pool, slice(_rate_method_id, 0, 4))


@internal
def _get_and_approve_coins(_pool: address, _n_coins: int128, _is_underlying: bool, _is_v1: bool) -> address[MAX_COINS]:
    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    _coin: address = ZERO_ADDRESS
    for i in range(MAX_COINS):
        if i == _n_coins:
            break
        ui: uint256 = convert(i, uint256)
        if _is_underlying:
            if _is_v1:
                _coin = CurvePoolV1(_pool).underlying_coins(i)
            else:
                _coin = CurvePool(_pool).underlying_coins(ui)
            self.pool_data[_pool].ul_coins[i] =_coin
        else:
            if _is_v1:
                _coin = CurvePoolV1(_pool).coins(i)
            else:
                _coin = CurvePool(_pool).coins(ui)
            self.pool_data[_pool].coins[i] = _coin
        if _coin != 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
            _response: Bytes[32] = raw_call(
                _coin,
                concat(
                    method_id("approve(address,uint256)"),
                    convert(_pool, bytes32),
                    convert(MAX_UINT256, bytes32),
                ),
                max_outsize=32,
            )
            if len(_response) != 0:
                assert convert(_response, bool)
        _coins[i] = _coin

    return _coins



@external
def add_pool(
    _pool: address,
    _n_coins: int128,
    _lp_token: address,
    _calculator: address,
    _rate_method_id: bytes32,
    _decimals: bytes32,
    _underlying_decimals: bytes32,
    _has_initial_A: bool,
    _is_v1: bool,
):
    """
    @notice Add a pool to the registry
    @dev Only callable by admin
    @param _pool Pool address to add
    @param _n_coins Number of coins in the pool
    @param _lp_token Pool deposit token address
    @param _rate_method_id Encoded four-byte function signature to query
                           coin rates, right padded to bytes32
    @param _decimals Coin decimal values, tightly packed as uint8 and right
                     padded as bytes32
    @param _underlying_decimals Underlying coin decimal values, tightly packed
                                as uint8 and right padded as bytes32
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.pool_data[_pool].coins[0] == ZERO_ADDRESS  # dev: pool exists

    _coins: address[MAX_COINS] = self._get_and_approve_coins(_pool, _n_coins, False, _is_v1)
    _ucoins: address[MAX_COINS] = self._get_and_approve_coins(_pool, _n_coins, True, _is_v1)

    self._add_pool(
        _pool,
        _n_coins,
        _lp_token,
        _calculator,
        _rate_method_id,
        _coins,
        _ucoins,
        _decimals,
        _underlying_decimals,
        _has_initial_A,
        _is_v1,
    )


@external
def add_pool_without_underlying(
    _pool: address,
    _n_coins: int128,
    _lp_token: address,
    _calculator: address,
    _rate_method_id: bytes32,
    _decimals: bytes32,
    _use_rates: bytes32,
    _has_initial_A: bool,
    _is_v1: bool,
):
    """
    @notice Add a pool to the registry
    @dev Only callable by admin
    @param _pool Pool address to add
    @param _n_coins Number of coins in the pool
    @param _lp_token Pool deposit token address
    @param _rate_method_id Encoded four-byte function signature to query
                           coin rates, right padded as bytes32
    @param _decimals Coin decimal values, tightly packed as uint8 and right
                     padded as bytes32
    @param _use_rates Boolean array indicating which coins use lending rates,
                      tightly packed and right padded as bytes32
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.pool_data[_pool].coins[0] == ZERO_ADDRESS  # dev: pool exists

    _coins: CoinList = empty(CoinList)
    _use_rates_mem: bytes32 = _use_rates

    _coins.coins = self._get_and_approve_coins(_pool, _n_coins, False, _is_v1)

    for i in range(MAX_COINS):
        if i == _n_coins:
            break
        # add underlying coin
        if not convert(slice(_use_rates_mem, convert(i, uint256), 1), bool):
            _coins.ucoins[i] = _coins.coins[i]
            self.pool_data[_pool].ul_coins[i] = _coins.ucoins[i]

    self._add_pool(
        _pool,
        _n_coins,
        _lp_token,
        _calculator,
        _rate_method_id,
        _coins.coins,
        _coins.ucoins,
        _decimals,
        EMPTY_BYTES32,
        _has_initial_A,
        _is_v1,
    )


@internal
def _remove_market(_pool: address, _coina: address, _coinb: address):
    _first: uint256 = min(convert(_coina, uint256), convert(_coinb, uint256))
    _second: uint256 = max(convert(_coina, uint256), convert(_coinb, uint256))

    _pool_zero: uint256 = self.markets[_first][_second][0]
    _length: uint256 = _pool_zero % 65536 - 1
    if _length == 0:
        self.markets[_first][_second][0] = 0
    elif shift(_pool_zero, -16) == convert(_pool, uint256):
        self.markets[_first][_second][0] = shift(self.markets[_first][_second][_length], 16) + _length
        self.markets[_first][_second][_length] = 0
    else:
        self.markets[_first][_second][0] = _pool_zero - 1
        for n in range(1, 65536):
            if n == convert(_length, int128):
                break
            if self.markets[_first][_second][n] == convert(_pool, uint256):
                self.markets[_first][_second][n] = self.markets[_first][_second][_length]
        self.markets[_first][_second][_length] = 0


@external
def remove_pool(_pool: address):
    """
    @notice Remove a pool to the registry
    @dev Only callable by admin
    @param _pool Pool address to remove
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.pool_data[_pool].coins[0] != ZERO_ADDRESS  # dev: pool does not exist

    # remove _pool from pool_list
    _location: uint256 = self.pool_data[_pool].location
    _length: uint256 = self.pool_count - 1

    if _location < _length:
        # replace _pool with final value in pool_list
        _addr: address = self.pool_list[_length]
        self.pool_list[_location] = _addr
        self.pool_data[_addr].location = _location

    # delete final pool_list value
    self.pool_list[_length] = ZERO_ADDRESS
    self.pool_count = _length

    _coins: CoinList = empty(CoinList)

    for i in range(MAX_COINS):
        _coins.coins[i] = self.pool_data[_pool].coins[i]
        if _coins.coins[i] == ZERO_ADDRESS:
            break

        # delete coin address from pool_data
        self.pool_data[_pool].coins[i] = ZERO_ADDRESS

        # delete underlying_coin from pool_data
        _coins.ucoins[i] = self.pool_data[_pool].ul_coins[i]
        self.pool_data[_pool].ul_coins[i] = ZERO_ADDRESS

    for i in range(MAX_COINS):
        if _coins.coins[i] == ZERO_ADDRESS:
            break

        # remove pool from markets
        for x in range(i, i + MAX_COINS):
            if x == i:
                continue
            if _coins.coins[x] == ZERO_ADDRESS:
                break

            self._remove_market(_pool, _coins.coins[i], _coins.coins[x])

            if _coins.ucoins[i] != _coins.coins[i] or _coins.ucoins[x] != _coins.coins[x]:
                self._remove_market(_pool, _coins.ucoins[i], _coins.ucoins[x])

    log PoolRemoved(_pool)


@external
def set_pool_gas_estimates(_addr: address[5], _amount: uint256[2][5]):
    """
    @notice Set gas estimate amounts
    @param _addr Array of pool addresses
    @param _amount Array of gas estimate amounts as `[(wrapped, underlying), ..]`
    """
    assert msg.sender == self.admin  # dev: admin-only function

    for i in range(5):
        if _addr[i] == ZERO_ADDRESS:
            break
        self.gas_estimate_values[_addr[i]] = _amount[i]


@external
def set_coin_gas_estimates(_addr: address[10], _amount: uint256[10]):
    """
    @notice Set gas estimate amounts
    @param _addr Array of coin addresses
    @param _amount Array of gas estimate amounts
    """
    assert msg.sender == self.admin  # dev: admin-only function

    for i in range(10):
        if _addr[i] == ZERO_ADDRESS:
            break
        self.gas_estimate_values[_addr[i]][0] = _amount[i]


@external
def set_gas_estimate_contract(_pool: address, _estimator: address):
    """
    @notice Set gas estimate contract
    @param _pool Pool address
    @param _estimator GasEstimator address
    """
    assert msg.sender == self.admin  # dev: admin-only function

    self.gas_estimate_contracts[_pool] = _estimator


@external
def set_calculator(_pool: address, _calculator: address):
    """
    @notice Set calculator contract
    @dev Used to calculate `get_dy` for a pool
    @param _pool Pool address
    @param _calculator `CurveCalc` address
    """
    assert msg.sender == self.admin  # dev: admin-only function

    self.pool_data[_pool].calculator = _calculator


@external
def set_liquidity_gauges(_pool: address, _liquidity_gauges: address[10]):
    """
    @notice Set liquidity gauge contracts``
    @param _pool Pool address
    @param _liquidity_gauges Liquidity gauge address
    """
    assert msg.sender == self.admin  # dev: admin-only function

    _lp_token: address = self.pool_data[_pool].lp_token
    _gauge_controller: address = self.gauge_controller
    for i in range(10):
        _gauge: address = _liquidity_gauges[i]
        if _gauge != ZERO_ADDRESS:
            assert LiquidityGauge(_gauge).lp_token() == _lp_token  # dev: wrong token
            GaugeController(_gauge_controller).gauge_types(_gauge)
            self.liquidity_gauges[_pool][i] = _gauge
        elif self.liquidity_gauges[_pool][i] != ZERO_ADDRESS:
            self.liquidity_gauges[_pool][i] = ZERO_ADDRESS
        else:
            break


@external
@view
def get_calculator(_pool: address) -> address:
    """
    @notice Get the calculator contract address for a pool
    @param _pool Pool address
    @return Calculator address
    """
    return self.pool_data[_pool].calculator


@external
def commit_transfer_ownership(_new_admin: address):
    """
    @notice Initiate a transfer of contract ownership
    @dev Once initiated, the actual transfer may be performed three days later
    @param _new_admin Address of the new owner account
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.transfer_ownership_deadline == 0  # dev: transfer already active

    _deadline: uint256 = block.timestamp + 3*86400
    self.transfer_ownership_deadline = _deadline
    self.future_admin = _new_admin

    log CommitNewAdmin(_deadline, _new_admin)


@external
def apply_transfer_ownership():
    """
    @notice Finalize a transfer of contract ownership
    @dev May only be called by the current owner, three days after a
         call to `commit_transfer_ownership`
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.transfer_ownership_deadline != 0  # dev: transfer not active
    assert block.timestamp >= self.transfer_ownership_deadline  # dev: now < deadline

    _new_admin: address = self.future_admin
    self.admin = _new_admin
    self.transfer_ownership_deadline = 0

    log NewAdmin(_new_admin)


@external
def revert_transfer_ownership():
    """
    @notice Revert a transfer of contract ownership
    @dev May only be called by the current owner
    """
    assert msg.sender == self.admin  # dev: admin-only function

    self.transfer_ownership_deadline = 0


@external
def claim_balance(_token: address):
    """
    @notice Transfer an ERC20 or ETH balance held by this contract
    @dev The entire balance is transferred to `self.admin`
    @param _token Token address
    """
    assert msg.sender == self.admin  # dev: admin-only function

    if _token == 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE:
        send(msg.sender, self.balance)
    else:
        _balance: uint256 = ERC20(_token).balanceOf(self)
        _response: Bytes[32] = raw_call(
            _token,
            concat(
                method_id("transfer(address,uint256)"),
                convert(msg.sender, bytes32),
                convert(_balance, bytes32),
            ),
            max_outsize=32,
        )
        if len(_response) != 0:
            assert convert(_response, bool)
