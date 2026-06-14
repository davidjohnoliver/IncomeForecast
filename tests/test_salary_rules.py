import salary_rules
import pytest
import model

def standard_previous_deltas():
    return model.deltas_state.from_year(1999)

def standard_previous_funds():
    return model.funds_state(0, 0, 1999, 0.0, 0.0, 0.0)

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

def matched_deltas(gross_salary, rrsp, rrsp_available_room):
    deltas = model.deltas_state.from_year(2000)
    deltas = deltas.update_gross_salary(gross_salary)
    deltas = deltas.update_rrsp(rrsp)
    deltas = deltas.update_rrsp_available_room(rrsp_available_room)
    return deltas

def test_rrsp_matching_under_cap_and_room():
    rule = salary_rules.get_rrsp_matching(matching_cap_fraction=0.05)

    deltas = matched_deltas(gross_salary=100000, rrsp=3000, rrsp_available_room=20000)
    output = rule(deltas, standard_previous_funds(), standard_previous_deltas())

    # Match is the full employee contribution (3000 <= cap of 5000 and remaining room of 17000)
    assert 6000 == output.rrsp
    assert 3000 == output.benefits

def test_rrsp_matching_limited_by_cap():
    rule = salary_rules.get_rrsp_matching(matching_cap_fraction=0.05)

    deltas = matched_deltas(gross_salary=100000, rrsp=8000, rrsp_available_room=20000)
    output = rule(deltas, standard_previous_funds(), standard_previous_deltas())

    # Match is capped at 5% of salary = 5000
    assert 13000 == output.rrsp
    assert 5000 == output.benefits

def test_rrsp_matching_limited_by_rrsp_room():
    rule = salary_rules.get_rrsp_matching(matching_cap_fraction=0.05)

    deltas = matched_deltas(gross_salary=100000, rrsp=3000, rrsp_available_room=4000)
    output = rule(deltas, standard_previous_funds(), standard_previous_deltas())

    # Only 1000 of room remains after the employee's 3000 contribution
    assert 4000 == output.rrsp
    assert 1000 == output.benefits

def test_rrsp_matching_no_room_left():
    rule = salary_rules.get_rrsp_matching(matching_cap_fraction=0.05)

    deltas = matched_deltas(gross_salary=100000, rrsp=5000, rrsp_available_room=5000)
    output = rule(deltas, standard_previous_funds(), standard_previous_deltas())

    # Employee already exhausted the room, so there's no match
    assert 5000 == output.rrsp
    assert 0 == output.benefits

def test_rrsp_matching_uses_carried_forward_room():
    rule = salary_rules.get_rrsp_matching(matching_cap_fraction=0.05)

    # No new room is generated this year, but room was carried forward from previous years.
    previous_funds = model.funds_state(0, 0, 1999, 0.0, 0.0, 10000)
    deltas = matched_deltas(gross_salary=100000, rrsp=3000, rrsp_available_room=0)
    output = rule(deltas, previous_funds, standard_previous_deltas())

    # 10000 carried-forward room less the employee's 3000 leaves 7000, enough for the full 3000 match
    assert 6000 == output.rrsp
    assert 3000 == output.benefits
