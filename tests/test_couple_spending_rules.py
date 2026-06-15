import model
import couple_spending_rules


def _couple_deltas(year, partner1_gross, partner2_gross, partner2_benefits, household_spending):
    partner1 = model.deltas_state.from_year(year).update_gross_salary(partner1_gross)
    partner2 = (
        model.deltas_state.from_year(year)
        .update_gross_salary(partner2_gross)
        .update_benefits(partner2_benefits)
    )
    return model.couple_deltas_state(
        partner1_deltas=partner1,
        partner2_deltas=partner2,
        household_spending=household_spending,
        household_debt_payments=0,
    )


def test_increasing_savings_excludes_previous_benefits_from_spendable_income():
    # The proportional-savings reference must be computed from spendable income, ie excluding employer RRSP matching
    # (which lands in benefits). Here last year's net income is 110000 of which 10000 is a (non-spendable) benefit, so
    # the spendable base is 100000 and the maintained savings rate is (100000 - 80000) / 100000 = 0.2.
    rule = couple_spending_rules.get_increasing_savings_increasing_spending(
        initial_year=1999, increase_savings_weight=0.5
    )

    previous_deltas = _couple_deltas(
        year=2005,
        partner1_gross=60000,
        partner2_gross=40000,
        partner2_benefits=10000,
        household_spending=80000,
    )
    current_deltas = _couple_deltas(
        year=2006,
        partner1_gross=70000,
        partner2_gross=50000,
        partner2_benefits=0,
        household_spending=0,
    )

    result = rule(current_deltas, None, previous_deltas)

    # ceiling = 120000 - 0.2 * 120000 = 96000; floor = 80000; sp = 0.5*96000 + 0.5*80000 = 88000.
    # (Including the 10000 benefit in the base would instead give ~83636, so this pins the exclusion.)
    assert 88000 == result.household_spending
