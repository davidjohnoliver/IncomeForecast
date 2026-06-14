import salary_rules
import pytest
import model
import natural_rules

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

def test_rrsp_matching_is_tax_neutral_via_refund():
    # The match adds equally to rrsp and benefits, so it cancels in taxable_income: next year's refund (from
    # apply_tax_refund) is identical to the no-match case and reflects only the employee's own contribution. This
    # guards the invariant that the match must be written to BOTH rrsp and benefits - writing to only one would make
    # apply_tax_refund over- or under-refund, since tax is applied (ignoring the match) before the match runs.
    rule = salary_rules.get_rrsp_matching(matching_cap_fraction=0.05)
    previous_funds = standard_previous_funds()
    previous_deltas = standard_previous_deltas()

    # Year 2000: employee contributes 10000; tax is applied before matching, mirroring the real rule order.
    no_match = matched_deltas(gross_salary=100000, rrsp=10000, rrsp_available_room=30000)
    no_match = natural_rules.apply_tax(no_match, previous_funds, previous_deltas)

    matched = rule(no_match, previous_funds, previous_deltas)

    # The employer matched 5000 (5% of salary), added to both rrsp and benefits.
    assert 15000 == matched.rrsp
    assert 5000 == matched.benefits
    # Tax was computed before the match; the match cancels in taxable_income, so both are unchanged.
    assert no_match.tax == matched.tax
    assert no_match.taxable_income == matched.taxable_income

    # The refund computed the following year is identical whether or not the employer matched.
    next_year = model.deltas_state.from_year(2001)
    refund_matched = natural_rules.apply_tax_refund(next_year, previous_funds, matched).tax_refund
    refund_no_match = natural_rules.apply_tax_refund(next_year, previous_funds, no_match).tax_refund
    assert refund_matched == refund_no_match
    assert refund_matched > 0
