import spending_rules
import model
import math

def standard_previous_deltas():
    return model.deltas_state.from_year(1999)

def standard_previous_funds():
    return model.funds_state(0, 0, 1999)

def test_get_luxury_over_basic():
    rule = spending_rules.get_luxury_over_basic(20000, 0.05)
    new_delta = model.get_updated_deltas_from_rules(standard_previous_funds(), standard_previous_deltas().update_spending(50000), [rule])
    assert 51500 == new_delta.spending

def test_get_luxury_over_basic_capped_below():
    rule = spending_rules.get_luxury_over_basic_capped(20000, 0.05, 0.9)
    def set_salary(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(100000)
    new_delta = model.get_updated_deltas_from_rules(standard_previous_funds(), standard_previous_deltas().update_spending(50000), [set_salary, rule])
    assert 51500 == new_delta.spending

def test_get_luxury_over_basic_capped_above():
    rule = spending_rules.get_luxury_over_basic_capped(20000, 0.05, 0.9)
    def set_salary(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(55800)
    new_delta = model.get_updated_deltas_from_rules(standard_previous_funds(), standard_previous_deltas().update_spending(50000), [set_salary, rule])
    assert 50220 == new_delta.spending

def test_get_maxed_or_zeroed_out():
    end_region = 0.1
    c_m = 0.3

    assert c_m == spending_rules.get_maxed_or_zeroed_out(0.5, c_m, end_region)
    assert c_m == spending_rules.get_maxed_or_zeroed_out(0.1, c_m, end_region)
    assert math.isclose(c_m, spending_rules.get_maxed_or_zeroed_out(0.9, c_m, end_region))
    assert 0 == spending_rules.get_maxed_or_zeroed_out(0, c_m, end_region)
    assert 1 == spending_rules.get_maxed_or_zeroed_out(1, c_m, end_region)
    assert c_m / 2 == spending_rules.get_maxed_or_zeroed_out(0.05, c_m, end_region)
    assert c_m / 2 == spending_rules.get_maxed_or_zeroed_out(0.05, c_m, end_region)