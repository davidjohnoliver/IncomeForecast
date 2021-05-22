import model

def test_calculated_delta_values():
    deltas = model.deltas_state.from_year(1999)
    deltas = deltas.update_gross_salary(30000)
    deltas = deltas.update_tax(19000)
    deltas = deltas.update_tax_refund(700)
    deltas = deltas.update_spending(60)
    assert 11700 == deltas.total_net_income
    assert 11640 == deltas.undifferentiated_savings    

def test_get_updated_funds_from_deltas():
    year = 2040
    previous_funds = model.funds_state(1200, 1010, year)
    deltas = model.deltas_state.from_year(year + 1)
    deltas = deltas.update_rrsp(400)
    deltas = deltas.update_tfsa(333)
    new_funds = model.get_updated_funds_from_deltas(previous_funds, deltas)
    assert new_funds.rrsp_savings == 1600
    assert new_funds.tfsa_savings == 1343
    assert new_funds.year == 2041


def test_get_updated_deltas_from_rules():
    def set_rrsp_rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_rrsp(320)

    def set_gross_salary_rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(109)

    def double_rrsp_rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_rrsp(deltas.rrsp * 2)

    year = 1999
    new_deltas = model.get_updated_deltas_from_rules(model.funds_state(
        0, 0, year), model.deltas_state.from_year(year), [set_rrsp_rule, set_gross_salary_rule, double_rrsp_rule])

    assert new_deltas.year == 2000
    assert new_deltas.gross_salary == 109
    assert new_deltas.rrsp == 640

def test_couple_rule_from_single_rule():
    def set_gross_salary_rule_partner_1(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(previous_deltas.gross_salary + 20)
        
    def set_gross_salary_rule_partner_2(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(previous_deltas.gross_salary + 18)

    previous_deltas = model.couple_deltas_state.from_year(1980)
    previous_deltas = previous_deltas.update_partner1_deltas(previous_deltas.partner1_deltas.update_gross_salary(14))
    previous_deltas = previous_deltas.update_partner2_deltas(previous_deltas.partner2_deltas.update_gross_salary(7))

    assert previous_deltas.partner1_deltas.gross_salary == 14
    assert previous_deltas.partner2_deltas.gross_salary == 7

    rules = [
        model.get_couple_rule_from_single_rule(set_gross_salary_rule_partner_1, 1),
        model.get_couple_rule_from_single_rule(set_gross_salary_rule_partner_2, 2),
    ]

    deltas = model.get_updated_couple_deltas_from_rules(model.couple_funds_state.from_savings(0,0,0,1980), previous_deltas, rules)

    assert deltas.year == 1981

    assert deltas.partner1_deltas.gross_salary == 34
    assert deltas.partner2_deltas.gross_salary == 25