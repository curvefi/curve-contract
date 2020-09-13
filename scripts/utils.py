from typing import List


def pack_values(values: List[int]) -> bytes:
    """
    Tightly pack integer values as a `bytes32` value prior to calling `Registry.add_pool`

    Arguments
    ---------
    values : list
        List of integer values to pack

    Returns
    -------
    bytes
        Bytestring of tightly packed values, right padded right to 32 bytes
    """
    packed = b"".join(i.to_bytes(1, "big") for i in values)
    padded = packed + bytes(32 - len(values))
    return padded


def right_pad(hexstring: str) -> str:
    """
    Right-pad a hex string to 32 bytes.

    Arguments
    ---------
    hexstring : str
        Hex string to be padded

    Returns
    -------
    str
        Hex string right padded to 32 bytes
    """
    length = len(hexstring) // 2 - 1
    pad_amount = 32 - length
    return f"{hexstring}{'00'*pad_amount}"
