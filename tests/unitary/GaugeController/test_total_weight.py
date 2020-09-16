

TYPE_WEIGHTS = [5 * 10 ** 17, 2 * 10 ** 18]
GAUGE_WEIGHTS = [2 * 10 ** 18, 10 ** 18, 5 * 10 ** 17]


def test_total_weight(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.add_gauge(three_gauges[0], 0, GAUGE_WEIGHTS[0], {'from': accounts[0]})

    assert gauge_controller.get_total_weight() == (GAUGE_WEIGHTS[0]*TYPE_WEIGHTS[0])


def test_change_type_weight(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.add_gauge(three_gauges[0], 0, 10**18, {'from': accounts[0]})

    gauge_controller.change_type_weight(0, 31337, {'from': accounts[0]})

    assert gauge_controller.get_total_weight() == 10**18 * 31337


def test_change_gauge_weight(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.add_gauge(three_gauges[0], 0, 10**18, {'from': accounts[0]})

    gauge_controller.change_gauge_weight(three_gauges[0], 31337, {'from': accounts[0]})

    assert gauge_controller.get_total_weight() == TYPE_WEIGHTS[0] * 31337


def test_multiple(accounts, chain, gauge_controller, three_gauges):
    gauge_controller.add_type(b'Insurance', TYPE_WEIGHTS[1], {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[0], 0, GAUGE_WEIGHTS[0], {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[1], 0, GAUGE_WEIGHTS[1], {'from': accounts[0]})
    gauge_controller.add_gauge(three_gauges[2], 1, GAUGE_WEIGHTS[2], {'from': accounts[0]})

    expected = (
        (GAUGE_WEIGHTS[0]*TYPE_WEIGHTS[0]) +
        (GAUGE_WEIGHTS[1]*TYPE_WEIGHTS[0]) +
        (GAUGE_WEIGHTS[2]*TYPE_WEIGHTS[1])
    )

    assert gauge_controller.get_total_weight() == expected
