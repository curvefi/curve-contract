pragma solidity ^0.5.0;


interface IERC20 {
    function transferFrom(address, address, uint256) external;
}

contract AaveLendingPoolMock {

    uint16 public lastReferral;

    mapping (address => address) aTokens;

    function _add_token(address _underlying, address _aToken) external {
        aTokens[_underlying] = _aToken;
    }

    /**
    * @dev deposits The underlying asset into the reserve. A corresponding amount
           of the overlying asset (aTokens) is minted.
    * @param _reserve the address of the reserve
    * @param _amount the amount to be deposited
    * @param _referralCode integrators are assigned a referral code and can potentially receive rewards.
    **/
    function deposit(address _reserve, uint256 _amount, uint16 _referralCode) external payable {
        require (aTokens[_reserve] != address(0));
        lastReferral = _referralCode;
        IERC20(_reserve).transferFrom(msg.sender, aTokens[_reserve], _amount);
    }

}
