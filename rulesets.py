"""
Defined model rulesets.
"""
import ruleset
import salary_rules
import savings_rules
import spending_rules
import solve

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

def curie(
    salary_compound_rate : float, 
    salary_plateau : float, 
    base_spending : float, 
    spending_luxury_compound_rate : float, 
    cap_fractional : float,
    initial_year : int, 
    year_of_retirement : int, 
    year_of_death : int,
    retirement_income : float,
    rrsp_interest_rate : float,
    tfsa_interest_rate : float,
    optimize : solve.Optimizing_Solver
    ):
    """
    A ruleset with similar rules to B, but attempting to optimize the RRSP/TFSA split, both for savings during career and also for 
    deductions during retirement.

    Remarks: Optimizing with the `luxury_over_basic_capped` spending rule proved unsatisfying because it's too easy to use spending 
    parameters for which no solution can be found.
    """
    career_length_yrs = year_of_retirement - initial_year
    retirement_length_yrs = year_of_death - year_of_retirement

    initial_rrsp_func = optimize.subscribe_optimized_scalar("initial_rrsp", lower_bound=0, upper_bound=1, initial_guess=0.5)
    final_rrsp_func = optimize.subscribe_optimized_scalar("final_rrsp", lower_bound=0, upper_bound=1, initial_guess=0.5)
    initial_rrsp_retirement_func = optimize.subscribe_optimized_scalar("initial_rrsp_retirement", lower_bound=0, upper_bound=1, initial_guess=0.5)
    final_rrsp_retirement_func = optimize.subscribe_optimized_scalar("final_rrsp_retirement", lower_bound=0, upper_bound=1, initial_guess=0.5)
    
    return (
        ruleset.get_career_rules(
            salary_rules.get_compound_plateau(salary_compound_rate, salary_plateau),
            spending_rules.get_luxury_over_basic_capped(base_spending, spending_luxury_compound_rate, cap_fractional),
            savings_rules.get_simple_linear_func(initial_rrsp_func, final_rrsp_func, initial_year, career_length_yrs, optimize.set_failed),
            rrsp_interest_rate,
            tfsa_interest_rate
        ),
        ruleset.get_retirement_rules(
            retirement_income,
            savings_rules.get__linear_retirement_deduction_func(
                initial_rrsp_retirement_func, 
                final_rrsp_retirement_func, 
                year_of_retirement, 
                retirement_length_yrs, 
                optimize.set_failed
            ),
            rrsp_interest_rate,
            tfsa_interest_rate
        )
    )

def dirac(
    salary_compound_rate : float, 
    salary_plateau : float, 
    base_spending : float, 
    spending_luxury_compound_rate : float, 
    cap_fractional : float,
    initial_year : int, 
    year_of_retirement : int, 
    year_of_death : int,
    retirement_income : float,
    rrsp_interest_rate : float,
    tfsa_interest_rate : float,
    optimize : solve.Optimizing_Solver
    ):
    """
    A ruleset with similar rules to B, but attempting to optimize the RRSP/TFSA split, only for savings during career.

    Remarks: Created mainly to try to understand the problems with C. Optimizing with the `luxury_over_basic_capped` spending rule proved unsatisfying because it's too easy to use spending 
    parameters for which no solution can be found.
    """
    career_length_yrs = year_of_retirement - initial_year

    initial_rrsp_func = optimize.subscribe_optimized_scalar("initial_rrsp", lower_bound=0, upper_bound=1, initial_guess=0.5)
    final_rrsp_func = optimize.subscribe_optimized_scalar("final_rrsp", lower_bound=0, upper_bound=1, initial_guess=0.5)
    
    return (
        ruleset.get_career_rules(
            salary_rules.get_compound_plateau(salary_compound_rate, salary_plateau),
            spending_rules.get_luxury_over_basic_capped(base_spending, spending_luxury_compound_rate, cap_fractional),
            savings_rules.get_simple_linear_func(initial_rrsp_func, final_rrsp_func, initial_year, career_length_yrs, optimize.set_failed),
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

def einstein(
    salary_compound_rate : float, 
    salary_plateau : float, 
    base_spending : float, 
    increase_savings_weight : float,
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
    Non-optimizing ruleset which uses the increasing_savings_increasing_spending rule for spending.
    """
    career_length_yrs = year_of_retirement - initial_year
    return (
        ruleset.get_career_rules(
            salary_rules.get_compound_plateau(salary_compound_rate, salary_plateau),
            spending_rules.get_increasing_savings_increasing_spending(initial_year, increase_savings_weight),
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

def franklin(
    salary_compound_rate : float, 
    salary_plateau : float, 
    base_spending : float, 
    increase_savings_weight : float,
    initial_rrsp_allotment : float, 
    final_rrsp_allotment : float, 
    initial_year : int, 
    year_of_retirement : int, 
    year_of_death : int,
    retirement_income : float,
    rrsp_interest_rate : float,
    tfsa_interest_rate : float,
    optimize : solve.Optimizing_Solver
    ):
    """
    Ruleset which uses the increasing_savings_increasing_spending rule for spending, and optimizes RRSP/TFSA split for career savings.
    """
    career_length_yrs = year_of_retirement - initial_year

    initial_rrsp_func = optimize.subscribe_optimized_scalar("initial_rrsp", lower_bound=0, upper_bound=1, initial_guess=0.5)
    final_rrsp_func = optimize.subscribe_optimized_scalar("final_rrsp", lower_bound=0, upper_bound=1, initial_guess=0.5)

    return (
        ruleset.get_career_rules(
            salary_rules.get_compound_plateau(salary_compound_rate, salary_plateau),
            spending_rules.get_increasing_savings_increasing_spending(initial_year, increase_savings_weight),
            savings_rules.get_simple_linear_func(initial_rrsp_func, final_rrsp_func, initial_year, career_length_yrs, optimize.set_failed),
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