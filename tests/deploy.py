from os.path import realpath, dirname, join, splitext
from vyper import compile_code

CONTRACT_PATH = join(dirname(dirname(realpath(__file__))), 'vyper')


def deploy_contract(w3, filename, account, *args):
    if isinstance(filename, list):
        interface_files = filename[1:]
        filename = filename[0]
    else:
        interface_files = []

    with open(join(CONTRACT_PATH, filename)) as f:
        source = f.read()
    interface_codes = {}
    for i in interface_files:
        name = splitext(i)[0]
        with open(join(CONTRACT_PATH, i)) as f:
            interface_codes[name] = {
                    'type': 'vyper',
                    'code': f.read()}

    code = compile_code(source, ['bytecode', 'abi'],
                        interface_codes=interface_codes or None)
    deploy = w3.eth.contract(abi=code['abi'],
                             bytecode=code['bytecode'])
    tx_hash = deploy.constructor(*args).transact({'from': account, 'gas': 6 * 10**6})
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    return w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=deploy.abi)
