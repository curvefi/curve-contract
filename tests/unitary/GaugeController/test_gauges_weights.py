import brownie

WEEK = 7 * 86400
YEAR = 365 * 86400

TYPE_WEIGHTS = [5 * 10 ** 17, 2 * 10 ** 18]
GAUGE_WEIGHTS = [2 * 10 ** 18, 10 ** 18, 5 * 10 ** 17]


def test_add_gauges(accounts, gauge_controller, three_gauges):
    gauge_controller.add_gauge(three_gauges[0], 0, {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[1], 0, {'from': accounts[0]})

    assert gauge_controller.gauges(0) == three_gauges[0]
    assert gauge_controller.gauges(1) == three_gauges[1]


def test_n_gauges(accounts, gauge_controller, three_gauges):
    assert gauge_controller.n_gauges() == 0

    gauge_controller.add_gauge(three_gauges[0], 0, {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[1], 0, {'from': accounts[0]})

    assert gauge_controller.n_gauges() == 2


def test_n_gauges_same_gauge(accounts, gauge_controller, three_gauges):

    assert gauge_controller.n_gauges() == 0
    gauge_controller.add_gauge(three_gauges[0], 0, {'from': accounts[0]})
    with brownie.reverts('dev: cannot add the same gauge twice'):
        gauge_controller.add_gauge(three_gauges[0], 0, {'from': accounts[0]})

    assert gauge_controller.n_gauges() == 1


def test_n_gauge_types(gauge_controller, accounts, three_gauges):
    assert gauge_controller.n_gauge_types() == 1

    gauge_controller.add_type(b'Insurance', {'from': accounts[0]})

    assert gauge_controller.n_gauge_types() == 2


def test_gauge_types(accounts, gauge_controller, three_gauges):
    gauge_controller.add_type(b'Insurance', {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[0], 1, {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[1], 0, {'from': accounts[0]})

    assert gauge_controller.gauge_types(three_gauges[0]) == 1
    assert gauge_controller.gauge_types(three_gauges[1]) == 0


def test_gauge_weight(accounts, gauge_controller, gauge):
    gauge_controller.add_gauge(gauge, 0, 10**19, {'from': accounts[0]})

    assert gauge_controller.get_gauge_weight.call(gauge) == 10**19


def test_gauge_weight_as_zero(accounts, gauge_controller, gauge):
    gauge_controller.add_gauge(gauge, 0, {'from': accounts[0]})

    assert gauge_controller.get_gauge_weight.call(gauge) == 0


def test_set_gauge_weight(chain, accounts, gauge_controller, gauge):
    gauge_controller.add_gauge(gauge, 0, {'from': accounts[0]})
    gauge_controller.change_gauge_weight(gauge, 10**21)
    chain.sleep(WEEK)

    assert gauge_controller.get_gauge_weight(gauge) == 10**21


def test_type_weight(accounts, gauge_controller):
    gauge_controller.add_type(b'Insurance', {'from': accounts[0]})

    assert gauge_controller.get_type_weight(0) == TYPE_WEIGHTS[0]
    assert gauge_controller.get_type_weight(1) == 0


def test_change_type_weight(accounts, gauge_controller):
    gauge_controller.add_type(b'Insurance', {'from': accounts[0]})

    gauge_controller.change_type_weight(1, TYPE_WEIGHTS[1], {'from': accounts[0]})
    gauge_controller.change_type_weight(0, 31337, {'from': accounts[0]})

    assert gauge_controller.get_type_weight(0) == 31337
    assert gauge_controller.get_type_weight(1) == TYPE_WEIGHTS[1]


def test_relative_weight_write(accounts, chain, gauge_controller, three_gauges, skip_coverage):
    gauge_controller.add_type(b'Insurance', TYPE_WEIGHTS[1], {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[0], 0, GAUGE_WEIGHTS[0], {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[1], 0, GAUGE_WEIGHTS[1], {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[2], 1, GAUGE_WEIGHTS[2], {'from': accounts[0]})

    total_weight = TYPE_WEIGHTS[0] * GAUGE_WEIGHTS[0] + \
        TYPE_WEIGHTS[0] * GAUGE_WEIGHTS[1] + TYPE_WEIGHTS[1] * GAUGE_WEIGHTS[2]

    chain.sleep(int(1.1 * YEAR))

    # Fill weights and check that nothing has changed
    t = chain.time()
    for gauge, w, gauge_type in zip(three_gauges, GAUGE_WEIGHTS, [0, 0, 1]):
        gauge_controller.gauge_relative_weight_write(gauge, t)
        relative_weight = gauge_controller.gauge_relative_weight(gauge, t)
        assert relative_weight == 10 ** 18 * w * TYPE_WEIGHTS[gauge_type] / total_weight
