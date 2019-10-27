import model
import savings_rules

def test_simple_linear():
    rule = savings_rules.get_simple_linear(0, 1, 1999, 10)

    deltas_1999 = model.deltas_state.from_year(1999)
    deltas_1999 = deltas_1999.update_gross_salary(4000)
    assert 4000 == deltas_1999.undifferentiated_savings

    deltas = rule(deltas_1999, None, None)
    assert 0 == deltas.rrsp
    assert 4000 == deltas.tfsa

    deltas_2000 = model.deltas_state.from_year(2000)
    deltas_2000 = deltas_2000.update_gross_salary(4000)
    assert 4000 == deltas_2000.undifferentiated_savings
    
    deltas = rule(deltas_2000, None, None)
    assert 400 == deltas.rrsp
    assert 3600 == deltas.tfsa

def test_simple_retirement_deduction_excess_tfsa():
    rule = savings_rules.get_simple_retirement_deduction(retirement_year=2040, year_of_death=2060)
    deltas_2041 = model.deltas_state.from_year(2041)
    funds_2040 = model.funds_state(320000, 550000, 2040)

    deltas_2041 = deltas_2041.update_spending(40000)

    deltas = deltas_2041
    previous_funds = funds_2040
    previous_deltas = None
    deltas = rule(deltas, previous_funds, previous_deltas)
    assert -16000 == deltas.rrsp
    assert -24000 == deltas.tfsa

def test_simple_retirement_deduction_exact_savings():
    retirement_year = 2040
    year_of_death = 2060
    rule = savings_rules.get_simple_retirement_deduction(retirement_year, year_of_death)
    funds_2040 = model.funds_state(320000, 480000, 2040)

    spending = 40000

    previous_funds = funds_2040
    previous_deltas = None
    
    for y in range(retirement_year, year_of_death):
        year = y + 1
        deltas = model.deltas_state.from_year(year) \
            .update_spending(spending)
        deltas = rule(deltas, previous_funds, previous_deltas)
        funds = model.get_updated_funds_from_deltas(previous_funds, deltas)
        previous_deltas = deltas
        previous_funds = funds
    
    assert year_of_death == funds.year
    assert 0 == funds.rrsp_savings
    assert 0 == funds.tfsa_savings