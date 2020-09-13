# @version 0.2.4

gauge_types_: HashMap[address, int128]


@view
@external
def gauge_types(_gauge: address) -> int128:
    assert self.gauge_types_[_gauge] != 0
    return self.gauge_types_[_gauge] - 1


@external
def _set_gauge_type(_gauge: address, _type: int128):
    self.gauge_types_[_gauge] = _type + 1
