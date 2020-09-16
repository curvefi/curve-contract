# @version ^0.2.0
# @version 0.2.4

MAX_COINS: constant(int128) = 8


struct PoolArray:
    location: uint256
    decimals: bytes32
    rate_method_id: bytes32
    lp_token: address
    coins: address[MAX_COINS]
    ul_coins: address[MAX_COINS]

struct PoolCoins:
    coins: address[MAX_COINS]
    underlying_coins: address[MAX_COINS]
    decimals: uint256[MAX_COINS]

struct PoolInfo:
    balances: uint256[MAX_COINS]
    underlying_balances: uint256[MAX_COINS]
    decimals: uint256[MAX_COINS]
    lp_token: address
    A: uint256
    fee: uint256


interface ERC20:
    def decimals() -> uint256: view
    def balanceOf(addr: address) -> uint256: view
    def approve(spender: address, amount: uint256) -> bool: nonpayable
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(spender: address, to: address, amount: uint256) -> bool: nonpayable

interface CurvePool:
    def A() -> uint256: view
    def fee() -> uint256: view
    def coins(i: int128) -> address: view
    def underlying_coins(i: int128) -> address: view
    def get_dy(i: int128, j: int128, dx: uint256) -> uint256: view
    def get_dy_underlying(i: int128, j: int128, dx: uint256) -> uint256: view
    def exchange(i: int128, j: int128, dx: uint256, min_dy: uint256): payable
    def exchange_underlying(i: int128, j: int128, dx: uint256, min_dy: uint256): payable

interface GasEstimator:
    def estimate_gas_used(_pool: address, _from: address, _to: address) -> uint256: view


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

pool_list: public(address[65536])   # master list of pools
pool_count: public(uint256)         # actual length of pool_list

pool_data: HashMap[address, PoolArray]
returns_none: HashMap[address, bool]

gas_estimate_values: HashMap[address, uint256]
gas_estimate_contracts: HashMap[address, address]

# mapping of coin -> coin -> pools for trading
# all addresses are converted to uint256 prior to storage. coin addresses are stored
# using the smaller value first. within each pool address array, the first value
# is shifted 16 bits to the left, and these 16 bits are used to store the array length.

markets: HashMap[uint256, HashMap[uint256, uint256[65536]]]


@external
def __init__(_returns_none: address[4]):
    """
    @notice Constructor function
    @param _returns_none Token addresses that return None on a successful transfer
    """
    self.admin = msg.sender
    for _addr in _returns_none:
        if _addr == ZERO_ADDRESS:
            break
        self.returns_none[_addr] = True


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

    if i == 0:
        _addr: uint256 = shift(self.markets[_first][_second][0], -16)
        return convert(convert(_addr, bytes32), address)

    return convert(convert(self.markets[_first][_second][i], bytes32), address)


@external
@view
def get_pool_coins(_pool: address) -> PoolCoins:
    """
    @notice Get information on coins in a pool
    @dev Empty values in the returned arrays may be ignored
    @param _pool Pool address
    @return Coin addresses, underlying coin addresses, underlying coin decimals
    """
    _coins: PoolCoins = PoolCoins({
        coins: empty(address[MAX_COINS]),
        underlying_coins: empty(address[MAX_COINS]),
        decimals: empty(uint256[MAX_COINS])
    })
    _decimals_packed: bytes32 = self.pool_data[_pool].decimals

    for i in range(MAX_COINS):
        _coins.coins[i] = self.pool_data[_pool].coins[i]
        if _coins.coins[i] == ZERO_ADDRESS:
            break
        _coins.decimals[i] = convert(slice(_decimals_packed, convert(31 - i, uint256), 1), uint256)
        _coins.underlying_coins[i] = self.pool_data[_pool].ul_coins[i]

    return _coins


@external
@view
def get_pool_info(_pool: address) -> PoolInfo:
    """
    @notice Get information on a pool
    @dev Reverts if the pool address is unknown
    @param _pool Pool address
    @return balances, underlying balances, underlying decimals, lp token, amplification coefficient, fees
    """
    _pool_info: PoolInfo = PoolInfo({
        balances: empty(uint256[MAX_COINS]),
        underlying_balances: empty(uint256[MAX_COINS]),
        decimals: empty(uint256[MAX_COINS]),
        lp_token: self.pool_data[_pool].lp_token,
        A: CurvePool(_pool).A(),
        fee: CurvePool(_pool).fee()
    })

    _decimals_packed: bytes32 = self.pool_data[_pool].decimals

    for i in range(MAX_COINS):
        _coin: address = self.pool_data[_pool].coins[i]
        if _coin == ZERO_ADDRESS:
            assert i != 0
            break
        _pool_info.decimals[i] = convert(slice(_decimals_packed, convert(31 - i, uint256), 1), uint256)
        _pool_info.balances[i] = ERC20(_coin).balanceOf(_pool)
        _underlying_coin: address = self.pool_data[_pool].ul_coins[i]
        if _coin == _underlying_coin:
            _pool_info.underlying_balances[i] = _pool_info.balances[i]
        elif _underlying_coin != ZERO_ADDRESS:
            _pool_info.underlying_balances[i] = ERC20(_underlying_coin).balanceOf(_pool)

    return _pool_info


@external
def get_pool_rates(_pool: address) -> uint256[MAX_COINS]:
    """
    @notice Get rates between coins and underlying coins
    @dev For coins where there is no underlying coin, or where
         the underlying coin cannot be swapped, the rate is
         given as 1e18
    @param _pool Pool address
    @return Rates between coins and underlying coins
    """
    _rates: uint256[MAX_COINS] = empty(uint256[MAX_COINS])
    _rate_method_id: Bytes[4] = slice(self.pool_data[_pool].rate_method_id, 0, 4)
    for i in range(MAX_COINS):
        _coin: address = self.pool_data[_pool].coins[i]
        if _coin == ZERO_ADDRESS:
            break
        if _coin == self.pool_data[_pool].ul_coins[i]:
            _rates[i] = 10 ** 18
        else:
            _response: Bytes[32] = raw_call(_coin, _rate_method_id, max_outsize=32)  # dev: bad response
            _rates[i] = convert(_response, uint256)

    return _rates


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
    _total: uint256 = 0
    _estimator: address = self.gas_estimate_contracts[_pool]
    if _estimator != ZERO_ADDRESS:
        return GasEstimator(_estimator).estimate_gas_used(_pool, _from, _to)

    for _addr in [_from, _pool, _to]:
        _gas: uint256 = self.gas_estimate_values[_addr]
        assert _gas != 0  # dev: value not set
        _total += _gas

    return _total


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
    j: int128 = -1
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
        if min(i, j) > -1:
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
        if i > -1 and j > -1:
            return i, j, True

    raise "No available market"


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
    else:
        return CurvePool(_pool).get_dy(i, j, _amount)


@external
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

    _initial_balance: uint256 = ERC20(_to).balanceOf(self)

    if self.returns_none[_from]:
        ERC20(_from).transferFrom(msg.sender, self, _amount)
    else:
        assert ERC20(_from).transferFrom(msg.sender, self, _amount)

    if _is_underlying:
        CurvePool(_pool).exchange_underlying(i, j, _amount, _expected)
    else:
        CurvePool(_pool).exchange(i, j, _amount, _expected)

    _received: uint256 = ERC20(_to).balanceOf(self) - _initial_balance

    if self.returns_none[_to]:
        ERC20(_to).transfer(msg.sender, _received)
    else:
        assert ERC20(_to).transfer(msg.sender, _received)

    log TokenExchange(msg.sender, _pool, _from, _to, _amount, _received)

    return True


# Admin functions

@external
def add_pool(
    _pool: address,
    _n_coins: int128,
    _lp_token: address,
    _decimals: uint256[MAX_COINS],
    _rate_method_id: Bytes[4],
    _use_underlying: bool = True,
    _use_rates: bool[MAX_COINS] = [False, False, False, False, False, False, False, False]
):
    """
    @notice Add a pool to the registry
    @dev Only callable by admin
    @param _pool Pool address to add
    @param _n_coins Number of coins in the pool
    @param _lp_token Pool deposit token address
    @param _decimals Underlying coin decimal values
    @param _rate_method_id Encoded function signature to query coin rates
    @param _use_underlying Use underlying_coins array when lending is used
    @param _use_rates If _use_underlying is False, define which coins should get lending rates
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.pool_data[_pool].coins[0] == ZERO_ADDRESS  # dev: pool exists

    # add pool to pool_list
    _length: uint256 = self.pool_count
    self.pool_list[_length] = _pool
    self.pool_count = _length + 1
    self.pool_data[_pool].location = _length
    self.pool_data[_pool].lp_token = _lp_token
    self.pool_data[_pool].rate_method_id = convert(_rate_method_id, bytes32)

    _decimals_packed: uint256 = 0

    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    _ucoins: address[MAX_COINS] = empty(address[MAX_COINS])

    for i in range(MAX_COINS):
        if i == _n_coins:
            break

        # add coin
        _coins[i] = CurvePool(_pool).coins(i)
        ERC20(_coins[i]).approve(_pool, MAX_UINT256)
        self.pool_data[_pool].coins[i] = _coins[i]

        # add underlying coin
        if _use_underlying:
            _ucoins[i] = CurvePool(_pool).underlying_coins(i)
            if _ucoins[i] != _coins[i]:
                ERC20(_ucoins[i]).approve(_pool, MAX_UINT256)
        else:
            if not _use_rates[i]:
                _ucoins[i] = _coins[i]

        self.pool_data[_pool].ul_coins[i] = _ucoins[i]

        # add decimals
        _value: uint256 = _decimals[i]
        if _value == 0:
            if _ucoins[i] == ZERO_ADDRESS:
                _value = ERC20(_coins[i]).decimals()
            else:
                _value = ERC20(_ucoins[i]).decimals()

        assert _value < 256  # dev: decimal overflow
        _decimals_packed += shift(_value, i * 8)

    for i in range(MAX_COINS):
        if i == _n_coins:
            break

        # add pool to markets
        for x in range(i, i + MAX_COINS):
            if x == i:
                continue
            if x == _n_coins:
                break

            _first: uint256 = min(convert(_coins[i], uint256), convert(_coins[x], uint256))
            _second: uint256 = max(convert(_coins[i], uint256), convert(_coins[x], uint256))

            _pool_zero: uint256 = self.markets[_first][_second][0]
            if _pool_zero != 0:
                _length = _pool_zero % 65536
                self.markets[_first][_second][_length] = convert(_pool, uint256)
                self.markets[_first][_second][0] = _pool_zero + 1
            else:
                self.markets[_first][_second][0] = shift(convert(_pool, uint256), 16) + 1

            if (_ucoins[i] == _coins[i] and _ucoins[x] == _coins[x]) or _ucoins[i] == ZERO_ADDRESS or _ucoins[x] == ZERO_ADDRESS:
                continue

            _first = min(convert(_ucoins[i], uint256), convert(_ucoins[x], uint256))
            _second = max(convert(_ucoins[i], uint256), convert(_ucoins[x], uint256))

            _pool_zero = self.markets[_first][_second][0]

            if _pool_zero != 0:
                _length = _pool_zero % 65536
                self.markets[_first][_second][_length] = convert(_pool, uint256)
                self.markets[_first][_second][0] = _pool_zero + 1
            else:
                self.markets[_first][_second][0] = shift(convert(_pool, uint256), 16) + 1

    self.pool_data[_pool].decimals = convert(_decimals_packed, bytes32)
    log PoolAdded(_pool, _rate_method_id)


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

    _coins: address[MAX_COINS] = empty(address[MAX_COINS])
    _ucoins: address[MAX_COINS] = empty(address[MAX_COINS])

    for i in range(MAX_COINS):
        _coins[i] = self.pool_data[_pool].coins[i]
        if _coins[i] == ZERO_ADDRESS:
            break

        # delete coin address from pool_data
        self.pool_data[_pool].coins[i] = ZERO_ADDRESS

        # delete underlying_coin from pool_data
        _ucoins[i] = self.pool_data[_pool].ul_coins[i]
        self.pool_data[_pool].ul_coins[i] = ZERO_ADDRESS

    for i in range(MAX_COINS):
        if _coins[i] == ZERO_ADDRESS:
            break

        # remove pool from markets
        for x in range(i, i + MAX_COINS):
            if x == i:
                continue
            if _coins[x] == ZERO_ADDRESS:
                break

            _first: uint256 = min(convert(_coins[i], uint256), convert(_coins[x], uint256))
            _second: uint256 = max(convert(_coins[i], uint256), convert(_coins[x], uint256))

            _pool_zero: uint256 = self.markets[_first][_second][0]
            _length = _pool_zero % 65536 - 1
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

            if _ucoins[i] == _coins[i] and _ucoins[x] == _coins[x]:
                continue

            _first = min(convert(_ucoins[i], uint256), convert(_ucoins[x], uint256))
            _second = max(convert(_ucoins[i], uint256), convert(_ucoins[x], uint256))
            _pool_zero = self.markets[_first][_second][0]
            _length = _pool_zero % 65536 - 1
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

    log PoolRemoved(_pool)


@external
def set_returns_none(_addr: address, _is_returns_none: bool):
    """
    @notice Set `returns_none` value for a coin
    @param _addr Coin address
    @param _is_returns_none if True, coin returns None on a successful transfer
    """
    assert msg.sender == self.admin  # dev: admin-only function

    self.returns_none[_addr] = _is_returns_none


@external
def set_gas_estimates(_addr: address[10], _amount: uint256[10]):
    """
    @notice Set gas estimate amounts
    @param _addr Array of pool or coin addresses
    @param _amount Array of gas estimate amounts
    """
    assert msg.sender == self.admin  # dev: admin-only function

    for i in range(10):
        if _addr[i] == ZERO_ADDRESS:
            break
        self.gas_estimate_values[_addr[i]] = _amount[i]


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
def commit_transfer_ownership(_new_admin: address):
    """
    @notice Initiate a transfer of contract ownership
    @dev Once initiated, the actual transfer may be performed three days later
    @param _new_admin Address of the new owner account
    """
    assert msg.sender == self.admin  # dev: admin-only function
    assert self.transfer_ownership_deadline == 0  # dev: transfer already active

    self.transfer_ownership_deadline = block.timestamp  # + 3*86400
    self.future_admin = _new_admin

    log CommitNewAdmin(block.timestamp, _new_admin)


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
def claim_token_balance(_token: address):
    """
    @notice Transfer any ERC20 balance held by this contract
    @dev The entire balance is transferred to `self.admin`
    @param _token Token address
    """
    assert msg.sender == self.admin  # dev: admin-only function

    _balance: uint256 = ERC20(_token).balanceOf(self)
    ERC20(_token).transfer(msg.sender, _balance)
