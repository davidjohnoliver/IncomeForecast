import utils

def test_HistoricValue_basic():
    hv = utils.HistoricValue(12.7, 1992)
    hv.set_latest_value(14.2)
    hv.set_latest_value(18.8)
    assert hv.values == (12.7, 14.2, 18.8)
    assert hv.initial_year == 1992
    assert hv.latest_year == 1994

    