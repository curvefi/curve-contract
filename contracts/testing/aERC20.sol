pragma solidity ^0.5.0;

import {AaveLendingPoolMock} from "./AaveLendingPoolMock.sol";

library SafeMath {
    function add(uint a, uint b) internal pure returns (uint c) {
        c = a + b;
        require(c >= a); // dev: overflow
    }
    function sub(uint a, uint b) internal pure returns (uint c) {
        require(b <= a); // dev: underflow
        c = a - b;
    }
    function mul(uint a, uint b) internal pure returns (uint c) {
        c = a * b;
        require(a == 0 || c / a == b); // dev: overflow
    }
    function div(uint a, uint b) internal pure returns (uint c) {
        require(b > 0); // dev: divide by zero
        c = a / b;
    }
}


interface IERC20 {
    function transfer(address, uint256) external;
    function transferFrom(address, address, uint256) external;
    function decimals() external returns (uint256);
    function _mint_for_testing(address, uint256) external;
}


contract ATokenMock {

    using SafeMath for uint256;

    string public symbol;
    string public name;
    uint256 public decimals;
    uint256 public totalSupply;

    address pool;
    uint256 public _get_rate;

    address lendingPool;
    IERC20 underlyingToken;

    mapping(address => uint256) balances;
    mapping(address => mapping(address => uint256)) allowed;

    event Transfer(address from, address to, uint256 value);
    event Approval(address owner, address spender, uint256 value);

    constructor(
        string memory _name,
        string memory _symbol,
        uint256 _decimals,
        address _underlyingToken,
        address _lendingPool
    )
        public
    {
        symbol = _symbol;
        name = _name;
        decimals = _decimals;
        underlyingToken = IERC20(_underlyingToken);
        lendingPool = _lendingPool;
        _get_rate = 10**18;
        AaveLendingPoolMock(_lendingPool)._add_token(_underlyingToken, address(this));
    }

    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
    }

    function allowance(
        address _owner,
        address _spender
    )
        public
        view
        returns (uint256)
    {
        return allowed[_owner][_spender];
    }

    function approve(address _spender, uint256 _value) public returns (bool) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function transfer(address _to, uint256 _value) public returns (bool) {
        balances[msg.sender] = balances[msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    function transferFrom(
        address _from,
        address _to,
        uint256 _value
    )
        public
        returns (bool)
    {
        balances[_from] = balances[_from].sub(_value);
        allowed[_from][msg.sender] = allowed[_from][msg.sender].sub(_value);
        balances[_to] = balances[_to].add(_value);
        emit Transfer(_from, _to, _value);
        return true;
    }

    function redeem(uint256 _amount) external {
        totalSupply = totalSupply.sub(_amount);
        balances[msg.sender] = balances[msg.sender].sub(_amount);
        underlyingToken.transfer(msg.sender, _amount);
        emit Transfer(msg.sender, address(0), _amount);
    }

    function mint(address _to, uint256 _amount) external {
        require(msg.sender == lendingPool);
        totalSupply = totalSupply.add(_amount);
        balances[_to] = balances[_to].add(_amount);
        emit Transfer(address(0), _to, _amount);
    }

    function _set_pool(address _pool) external {
        pool = _pool;
    }

    function set_exchange_rate(uint256 _rate) external {
        /**
            Because aTokens accrue balance instead of increasing their rate,
            we simulate a rate change by modifying the token balance of the pool
         */
        totalSupply = totalSupply.sub(balances[pool]);
        balances[pool] = balances[pool].mul(_rate).div(10**18);
        totalSupply = totalSupply.add(balances[pool]);
        _get_rate = _rate;
    }

    function _mint_for_testing(address _to, uint256 _amount) external {
        totalSupply = totalSupply.add(_amount);
        balances[_to] = balances[_to].add(_amount);
        underlyingToken._mint_for_testing(address(this), _amount);
        emit Transfer(address(0), _to, _amount);
    }

}
