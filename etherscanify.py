#!/usr/bin/env python3

from vyper.signatures.interface import extract_external_interface

N_COINS = 2
PRECISIONS = [10 ** 18, 10 ** 18]
contract_file = 'vyper/stableswap.vy'
interfaces = ['ERC20m', 'cERC20']
USE_LENDING = [True, False]
TETHERED = [False, False]
replacements = {
                '___N_COINS___': str(N_COINS),
                '___N_ZEROS___': '[' + ', '.join(['ZERO256'] * N_COINS) + ']',
                '___PRECISION_MUL___': '[' + ', '.join(
                    'convert(%s, uint256)' % (10 ** 18 // i) for i in PRECISIONS) + ']',
                '___USE_LENDING___': '[' + ', '.join(
                        str(i) for i in USE_LENDING) + ']',
                '___TETHERED___': '[' + ', '.join(
                        str(i) for i in TETHERED) + ']'}


with open(contract_file, 'r') as f:
    code = f.read()

    for k, v in replacements.items():
        code = code.replace(k, v)

    for interface in interfaces:
        interface_string = 'import {0} as {0}'.format(interface)
        interface_file = 'vyper/{0}.vy'.format(interface)
        with open(interface_file, 'r') as fi:
            interface_code = extract_external_interface(fi.read(), interface)
            interface_code = interface_code.replace(interface.capitalize(), interface)
            code = code.replace(interface_string, interface_code)

    with open('output.vy', 'w') as fo:
        fo.write(code)
