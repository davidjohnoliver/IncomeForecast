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


def test_get_quebec_pension_plan_contributes_before_retirement():
    rule = natural_rules.get_quebec_pension_plan(
        maximum_pensionable_earnings=68400,
        pension_contribution=0.07,
        current_monthly_pension_at_60=320,
        projected_monthly_pension_at_60=930,
        current_monthly_pension_at_65=415,
        projected_monthly_pension_at_65=1510,
        initial_year=2025,
        current_age=50,
        retirement_age=62,
        pension_start_age=63,
    )

    delta = model.deltas_state.from_year(2026)
    delta = delta.update_contributions(100)
    delta = rule(delta, None, None)

    assert math.isclose(4888, delta.contributions)
    assert 0 == delta.benefits


def test_get_quebec_pension_plan_pays_benefit_from_pension_start_age():
    rule = natural_rules.get_quebec_pension_plan(
        maximum_pensionable_earnings=68400,
        pension_contribution=0.07,
        current_monthly_pension_at_60=320,
        projected_monthly_pension_at_60=930,
        current_monthly_pension_at_65=415,
        projected_monthly_pension_at_65=1510,
        initial_year=2025,
        current_age=50,
        retirement_age=62,
        pension_start_age=63,
    )

    delta = model.deltas_state.from_year(2038)
    delta = delta.update_benefits(200)
    delta = rule(delta, None, None)

    actual_monthly_pension_at_60 = 930
    actual_monthly_pension_at_65 = 415 + (1510 - 415) * 0.8
    expected_monthly_pension = actual_monthly_pension_at_60 + (
        actual_monthly_pension_at_65 - actual_monthly_pension_at_60
    ) * 0.6

    assert 0 == delta.contributions
    assert math.isclose(200 + expected_monthly_pension * 12, delta.benefits)


def test_calculate_yearly_mortgage_payment():
    principal = 100000
    amortization = 25
    interest = 0.05
    # periodic_rate = (1 + 0.05/2)**(2/12) - 1 = 0.004123915
    # total_payments = 300
    # monthly = 100000 / ((1 - (1+periodic_rate)**-300) / periodic_rate) = 581.603
    # yearly = 6979.236
    expected_yearly_payment = 6979.236
    payment = natural_rules.calculate_yearly_mortgage_payment(principal, amortization, interest)
    assert math.isclose(expected_yearly_payment, payment, rel_tol=1e-5)


def test_get_mortgage_payment():
    principal = 100000
    amortization = 25
    interest = 0.05
    initial_year = 2021

    rule = natural_rules.get_mortgage_payment(principal, amortization, interest, initial_year)

    # Within amortization period
    delta = model.deltas_state.from_year(2021)
    delta = rule(delta, None, None)
    expected_yearly_payment = 6979.236
    assert math.isclose(expected_yearly_payment, delta.debt_payments, rel_tol=1e-5)

    # Final payment year (initial_year + amortization = 2046)
    delta_end = model.deltas_state.from_year(2046)
    delta_end = rule(delta_end, None, None)
    assert math.isclose(expected_yearly_payment, delta_end.debt_payments, rel_tol=1e-5)

    # After amortization period (initial_year + amortization + 1 = 2047)
    delta_after = model.deltas_state.from_year(2047)
    delta_after = rule(delta_after, None, None)
    assert delta_after.debt_payments == 0


def test_get_mortgage_payment_pays_full_amount_over_amortization():
    principal = 100000
    amortization = 25
    interest = 0.05
    initial_year = 2021

    rule = natural_rules.get_mortgage_payment(
        principal, amortization, interest, initial_year
    )
    yearly_payment = natural_rules.calculate_yearly_mortgage_payment(
        principal, amortization, interest
    )

    # The simulation applies rules starting the year after initial_year (initial_year itself is
    # the seed state), so iterate from initial_year + 1. Run for amortization + 5 years to confirm
    # that the full mortgage is paid and that payments stop once it is paid off.
    total_paid = 0.0
    payment_count = 0
    for year in range(initial_year + 1, initial_year + 1 + amortization + 5):
        delta = model.deltas_state.from_year(year)
        delta = rule(delta, None, None)
        total_paid += delta.debt_payments
        if delta.debt_payments > 0:
            payment_count += 1

    # Exactly `amortization` yearly payments are made, totalling the full amount of the mortgage.
    assert amortization == payment_count
    assert math.isclose(yearly_payment * amortization, total_paid)


def test_get_mortgage_payment_zero_interest():
    principal = 100000
    amortization = 25
    interest = 0.0
    initial_year = 2021

    rule = natural_rules.get_mortgage_payment(principal, amortization, interest, initial_year)

    delta = model.deltas_state.from_year(2021)
    delta = rule(delta, None, None)

    assert math.isclose(4000.0, delta.debt_payments)


def test_get_mortgage_payment_zero_amortization():
    with pytest.raises(ValueError, match="amortization_length must be greater than 0"):
        natural_rules.get_mortgage_payment(100000, 0, 0.05, 2021)
