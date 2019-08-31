import model
import savings_rules

def test_outputs():
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

