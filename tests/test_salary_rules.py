import salary_rules
import pytest
import model

def standard_previous_deltas():
    return model.deltas_state.from_year(1999)

def standard_previous_funds():
    return model.funds_state(0, 0, 1999)

def test_simple_increase():
    rule = salary_rules.get_compound_plateau(0.1, 80000)

    new_delta = model.get_updated_deltas_from_rules(standard_previous_funds(), standard_previous_deltas().update_gross_salary(40000), {rule})

    assert 44000 == new_delta.gross_salary

def test_does_plateau():
    rule = salary_rules.get_compound_plateau(0.1, 80000)

    deltas = standard_previous_deltas().update_gross_salary(40000)
    funds = standard_previous_funds()

    for _ in range(20):
        deltas = model.get_updated_deltas_from_rules(funds, deltas, {rule})
        funds = model.get_updated_funds_from_deltas(funds, deltas)

    assert 80000 == deltas.gross_salary
