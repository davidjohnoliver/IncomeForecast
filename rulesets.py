"""
Defined model rulesets.
"""
import ruleset
import salary_rules
import savings_rules
import spending_rules

def ampere(
    salary_compound_rate : float, 
    salary_plateau : float, 
    base_spending : float, 
    spending_luxury_compound_rate : float, 
    initial_rrsp_allotment : float, 
    final_rrsp_allotment : float, 
    initial_year : int, 
    year_of_retirement : int, 
    year_of_death : int,
    retirement_income : float,
    rrsp_interest_rate : float,
    tfsa_interest_rate : float
    ):
    """
    A complete ruleset based on simple, plausible models for spending and income growth.

    See the individual rules for an explanation of the input parameters.
    """
    career_length_yrs = year_of_retirement - initial_year
    return (
        ruleset.get_career_rules(
            salary_rules.get_compound_plateau(salary_compound_rate, salary_plateau),
            spending_rules.get_luxury_over_basic(base_spending, spending_luxury_compound_rate),
            savings_rules.get_simple_linear(initial_rrsp_allotment, final_rrsp_allotment, initial_year, career_length_yrs),
            rrsp_interest_rate,
            tfsa_interest_rate
        ),
        ruleset.get_retirement_rules(
            retirement_income,
            savings_rules.get_simple_retirement_deduction(year_of_retirement, year_of_death),
            rrsp_interest_rate,
            tfsa_interest_rate
        )
    )

def bose(
    salary_compound_rate : float, 
    salary_plateau : float, 
    base_spending : float, 
    spending_luxury_compound_rate : float, 
    cap_fractional : float,
    initial_rrsp_allotment : float, 
    final_rrsp_allotment : float, 
    initial_year : int, 
    year_of_retirement : int, 
    year_of_death : int,
    retirement_income : float,
    rrsp_interest_rate : float,
    tfsa_interest_rate : float
    ):
    """
    A complete ruleset based on simple, plausible models for spending and income growth. Spending is capped to some fraction of disposable income.

    See the individual rules for an explanation of the input parameters.
    """
    career_length_yrs = year_of_retirement - initial_year
    return (
        ruleset.get_career_rules(
            salary_rules.get_compound_plateau(salary_compound_rate, salary_plateau),
            spending_rules.get_luxury_over_basic_capped(base_spending, spending_luxury_compound_rate, cap_fractional),
            savings_rules.get_simple_linear(initial_rrsp_allotment, final_rrsp_allotment, initial_year, career_length_yrs),
            rrsp_interest_rate,
            tfsa_interest_rate
        ),
        ruleset.get_retirement_rules(
            retirement_income,
            savings_rules.get_simple_retirement_deduction(year_of_retirement, year_of_death),
            rrsp_interest_rate,
            tfsa_interest_rate
        )
    )