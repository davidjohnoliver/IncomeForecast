import ruleset
import salary_rules
import couple_savings_rules
import couple_spending_rules
import solve

def alice(
    partner1_salary_compound_rate : float, 
    partner1_salary_plateau : float, 
    partner2_salary_compound_rate : float, 
    partner2_salary_plateau : float, 
    base_spending : float, 
    spending_luxury_compound_rate : float,
    rrsp_interest_rate : float,
    tfsa_interest_rate : float
    ):
    """
    A dual-income ruleset which uses simple rules where possible, intended mainly for testing.
    """

    ruleset_func = ruleset.get_couple_ruleset(
        salary_rules.get_compound_plateau(partner1_salary_compound_rate, partner1_salary_plateau),
        salary_rules.get_compound_plateau(partner2_salary_compound_rate, partner2_salary_plateau),
        couple_spending_rules.get_luxury_over_basic(base_spending, spending_luxury_compound_rate),
        couple_savings_rules.get_equalizing_rrsp_only_split(),
        rrsp_interest_rate,
        tfsa_interest_rate
    )

    return ruleset_func
