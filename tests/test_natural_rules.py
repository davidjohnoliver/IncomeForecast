import pytest
import model
import natural_rules
import tax

@pytest.fixture(params=[0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000])
def gross_salary(request):
    return request.param

# -ve values correspond to withdrawing from RRSP after retirement (which is taxable)
@pytest.fixture(params=[0, 1000, 3000, 5000, 10000, 15000, -1000, -10000, -30000, -50000])
def rrsp(request):
    return request.param

def test_apply_tax(gross_salary, rrsp):
    if (rrsp > gross_salary):
        return # 
    
    taxable_income = gross_salary

    expected_income_tax = tax.get_income_tax(taxable_income)

    delta = model.deltas_state.from_year(1999)
    delta = delta.update_gross_salary(gross_salary)
    delta = delta.update_rrsp(rrsp)
    delta = natural_rules.apply_tax(delta, None, None)

    assert expected_income_tax == delta.tax

def test_apply_tax_refund(gross_salary, rrsp):
    previous_actual_taxable_income = gross_salary - rrsp

    paid_tax = tax.get_income_tax(gross_salary)
    correct_tax = tax.get_income_tax(previous_actual_taxable_income)
    expected_refund = paid_tax - correct_tax
    
    previous_delta = model.deltas_state.from_year(1999)
    previous_delta = previous_delta.update_gross_salary(gross_salary)
    previous_delta = previous_delta.update_rrsp(rrsp)
    previous_delta = natural_rules.apply_tax(previous_delta, None, None)

    delta = model.deltas_state.from_year(2000)

    delta = natural_rules.apply_tax_refund(delta, None, previous_delta)

    assert expected_refund == delta.tax_refund

