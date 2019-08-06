import spending_rules
import model

def standard_previous_deltas():
    return model.deltas_state.from_year(1999)

def standard_previous_funds():
    return model.funds_state(0, 0, 1999)

def test_simple_increase():
    rule = spending_rules.get_luxury_over_basic(20000, 0.05)
    new_delta = model.get_updated_deltas_from_rules(standard_previous_funds(), standard_previous_deltas().update_spending(50000), {rule})
    assert 51500 == new_delta.spending