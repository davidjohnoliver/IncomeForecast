import pytest
import math
import model
import natural_rules
import tax


@pytest.fixture(
    params=[0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
)
def gross_salary(request):
    return request.param


# -ve values correspond to withdrawing from RRSP after retirement (which is taxable)
@pytest.fixture(
    params=[0, 1000, 3000, 5000, 10000, 15000, -1000, -10000, -30000, -50000]
)
def rrsp(request):
    return request.param


@pytest.fixture(params=[0, 100, 500, 1000, 3000])
def rrsp_interest(request):
    return request.param


def test_apply_tax(gross_salary, rrsp):
    if rrsp > gross_salary:
        return  #

    taxable_income = gross_salary

    expected_income_tax = tax.get_income_tax(taxable_income)

    delta = model.deltas_state.from_year(1999)
    delta = delta.update_gross_salary(gross_salary)
    delta = delta.update_rrsp(rrsp)
    delta = natural_rules.apply_tax(delta, None, None)

    assert expected_income_tax == delta.tax


def test_apply_tax_with_unregistered_interest(gross_salary, rrsp):
    if rrsp > gross_salary:
        return  #

    interest = 2000
    taxable_income = gross_salary + interest

    expected_income_tax = tax.get_income_tax(taxable_income)

    delta = model.deltas_state.from_year(1999)
    delta = delta.update_gross_salary(gross_salary)
    delta = delta.update_rrsp(rrsp)
    delta = delta.update_unregistered_interest(interest)
    delta = natural_rules.apply_tax(delta, None, None)

    assert expected_income_tax == delta.tax


def test_apply_tax_refund(gross_salary, rrsp, rrsp_interest):
    previous_actual_taxable_income = gross_salary - rrsp

    paid_tax = tax.get_income_tax(gross_salary)
    correct_tax = tax.get_income_tax(previous_actual_taxable_income)
    expected_refund = paid_tax - correct_tax

    previous_delta = model.deltas_state.from_year(1999)
    previous_delta = previous_delta.update_gross_salary(gross_salary)
    previous_delta = previous_delta.update_rrsp(rrsp)
    previous_delta = previous_delta.update_rrsp_interest(rrsp_interest)
    previous_delta = natural_rules.apply_tax(previous_delta, None, None)

    delta = model.deltas_state.from_year(2000)

    delta = natural_rules.apply_tax_refund(delta, None, previous_delta)

    assert expected_refund == delta.tax_refund


def test_apply_tax_refund_with_unregistered_interest(gross_salary, rrsp, rrsp_interest):
    unregistered_interest = 2000
    previous_actual_taxable_income = gross_salary + unregistered_interest - rrsp

    paid_tax = tax.get_income_tax(gross_salary + unregistered_interest)
    correct_tax = tax.get_income_tax(previous_actual_taxable_income)
    expected_refund = paid_tax - correct_tax

    previous_delta = model.deltas_state.from_year(1999)
    previous_delta = previous_delta.update_gross_salary(gross_salary)
    previous_delta = previous_delta.update_rrsp(rrsp)
    previous_delta = previous_delta.update_rrsp_interest(rrsp_interest)
    previous_delta = previous_delta.update_unregistered_interest(unregistered_interest)
    previous_delta = natural_rules.apply_tax(previous_delta, None, None)

    delta = model.deltas_state.from_year(2000)

    delta = natural_rules.apply_tax_refund(delta, None, previous_delta)

    assert expected_refund == delta.tax_refund


def test_calculate_investment_interest():
    rule = natural_rules.get_calculate_investment_interest(
        rrsp_interest_rate=0.04, tfsa_interest_rate=0.07, unregistered_interest_rate=0.0
    )

    previous_funds = model.funds_state(12000, 19000, 1672, 0.0, 0.0, 0.0)

    delta = model.deltas_state.from_year(1673)
    delta = rule(delta, previous_funds, None)

    assert math.isclose(480, delta.rrsp_interest)
    assert math.isclose(1330, delta.tfsa_interest)

    funds = model.get_updated_funds_from_deltas(previous_funds, delta)

    assert math.isclose(12480, funds.rrsp_savings)
    assert math.isclose(20330, funds.tfsa_savings)


def test_calculate_investment_interest_with_unregistered():
    rule = natural_rules.get_calculate_investment_interest(
        rrsp_interest_rate=0.04,
        tfsa_interest_rate=0.07,
        unregistered_interest_rate=0.06,
    )

    previous_funds = model.funds_state(12000, 19000, 1672, 22000, 0.0, 0.0)

    delta = model.deltas_state.from_year(1673)
    delta = rule(delta, previous_funds, None)

    assert math.isclose(480, delta.rrsp_interest)
    assert math.isclose(1330, delta.tfsa_interest)
    assert math.isclose(1320, delta.unregistered_interest)

    funds = model.get_updated_funds_from_deltas(previous_funds, delta)

    assert math.isclose(12480, funds.rrsp_savings)
    assert math.isclose(20330, funds.tfsa_savings)
    assert math.isclose(23320, funds.unregistered_savings)


def test_increase_tfsa_available_room():
    rule = natural_rules.increase_tfsa_limit(500)

    previous_funds = model.funds_state(
        rrsp_savings=0.0,
        tfsa_savings=0.0,
        year=2000,
        unregistered_savings=0.0,
        tfsa_available_room=1000.0,
        rrsp_available_room=0.0,
    )

    delta = model.deltas_state.from_year(2001)
    delta = rule(delta, previous_funds, None)

    assert 500 == delta.tfsa_available_room

    funds = model.get_updated_funds_from_deltas(previous_funds, delta)

    assert 1500.0 == funds.tfsa_available_room


@pytest.mark.parametrize(
    "gross, income_fraction, annual_limit, expected",
    [
        (100000, 0.18, 20000, 18000),
        (200000, 0.18, 20000, 20000),
        (0, 0.18, 20000, 0),
    ],
)
def test_update_rrsp_available_room(gross, income_fraction, annual_limit, expected):
    rule = natural_rules.get_update_rrsp_limit(
        income_fraction=income_fraction, annual_limit=annual_limit
    )

    previous_funds = model.funds_state(
        rrsp_savings=0.0,
        tfsa_savings=0.0,
        year=1999,
        unregistered_savings=0.0,
        tfsa_available_room=0.0,
        rrsp_available_room=3000.0,
    )

    previous_delta = model.deltas_state.from_year(1999)
    previous_delta = previous_delta.update_gross_salary(gross)

    delta = model.deltas_state.from_year(2000)
    delta = rule(delta, previous_funds, previous_delta)

    assert math.isclose(expected, delta.rrsp_available_room)

    funds = model.get_updated_funds_from_deltas(previous_funds, delta)

    assert math.isclose(previous_funds.rrsp_available_room + expected, funds.rrsp_available_room)
