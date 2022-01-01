pragma solidity ^0.6.7;


contract RedemptionPriceSnapMock {
    uint256 internal internalSnappedRedemptionPrice;

    constructor() public {
        // Set redemption price to $1 (ray) so existing common tests which expect pegged coin can run.
        internalSnappedRedemptionPrice = 1000000000000000000000000000;
    }

    function setRedemptionPriceSnap(uint256 newPrice) external {
        internalSnappedRedemptionPrice = newPrice;
    }

    function snappedRedemptionPrice() public view returns (uint256) {
        return internalSnappedRedemptionPrice;
    }
}
