# @version 0.2.11
"""
@title Curve ETHX Pool Rate Calculator 
@author Curve.Fi
@license Copyright (c) Curve.Fi, 2021 - all rights reserved
@notice Logic for calculating exchange rate between ETHX -> ETH
"""

interface ETHX:
    def ratio() -> uint256: view


@view
@external
def get_rate(_coin: address) -> uint256:
    """
    @notice Calculate the exchange rate for 1 ETHX -> ETH
    @param _coin The ETHX contract address
    @return The exchange rate of 1 ETHX in ETH
    """
    result: uint256 = ETHX(_coin).ratio()
    return 10 ** 36 / result
