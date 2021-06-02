import ruleset
import salary_rules
import couple_savings_rules
import couple_spending_rules
from typing import Callable
import solve


def alice(
    partner1_salary_compound_rate: float,
    partner1_salary_plateau: float,
    partner2_salary_compound_rate: float,
    partner2_salary_plateau: float,
    base_spending: float,
    spending_luxury_compound_rate: float,
    rrsp_interest_rate: float,
    tfsa_interest_rate: float,
):
    """
    A dual-income ruleset which uses simple rules where possible, intended mainly for testing.
    """

    ruleset_func = ruleset.get_couple_ruleset(
        salary_rules.get_compound_plateau(
            partner1_salary_compound_rate, partner1_salary_plateau
        ),
        salary_rules.get_compound_plateau(
            partner2_salary_compound_rate, partner2_salary_plateau
        ),
        couple_spending_rules.get_luxury_over_basic(
            base_spending, spending_luxury_compound_rate
        ),
        couple_savings_rules.get_equalizing_rrsp_only_split(),
        rrsp_interest_rate,
        tfsa_interest_rate,
    )

    return ruleset_func


def _bad_seed_raw(
    partner1_salary_compound_rate: float,
    partner1_salary_plateau: float,
    partner2_salary_compound_rate: float,
    partner2_salary_plateau: float,
    initial_year: int,
    increase_savings_weight: float,
    initial_tfsa_func: Callable[[], float],
    final_tfsa_func: Callable[[], float],
    initial_equalize_income_weighting_func: Callable[[], float],
    final_equalize_income_weighting_func: Callable[[], float],
    partner1_year_of_retirement: int,
    partner2_year_of_retirement: int,
    final_year: int,
    rrsp_adjustment_func: Callable[[], float],
    rrsp_interest_rate: float,
    tfsa_interest_rate: float,
):

    ruleset_func = ruleset.get_couple_ruleset(
        salary_rules.get_compound_plateau(
            partner1_salary_compound_rate, partner1_salary_plateau
        ),
        salary_rules.get_compound_plateau(
            partner2_salary_compound_rate, partner2_salary_plateau
        ),
        couple_spending_rules.get_increasing_savings_increasing_spending(
            initial_year, increase_savings_weight
        ),
        couple_savings_rules.get_split_by_investment_then_partner(
            initial_tfsa_func,
            final_tfsa_func,
            initial_equalize_income_weighting_func,
            final_equalize_income_weighting_func,
            partner1_year_of_retirement,
            partner2_year_of_retirement,
            initial_year,
            final_year,
            rrsp_adjustment_func,
        ),
        rrsp_interest_rate,
        tfsa_interest_rate,
    )

    return ruleset_func


def bad_seed(
    partner1_salary_compound_rate: float,
    partner1_salary_plateau: float,
    partner2_salary_compound_rate: float,
    partner2_salary_plateau: float,
    initial_year: int,
    increase_savings_weight: float,
    initial_tfsa_guess: float,
    final_tfsa_guess: float,
    initial_equalize_income_weighting_guess: float,
    final_equalize_income_weighting_guess: float,
    partner1_year_of_retirement: int,
    partner2_year_of_retirement: int,
    final_year: int,
    rrsp_adjustment_guess: float,
    rrsp_interest_rate: float,
    tfsa_interest_rate: float,
    optimize: solve.Optimizing_Solver,
):
    """
    A dual-income ruleset which uses the increasing_savings_increasing_spending rule for spending vs. saving, and the split_by_investment_then_partner rule for savings allocations
    """

    initial_tfsa_func = optimize.subscribe_optimized_scalar(
        "initial_tfsa", 0, 1, initial_tfsa_guess
    )
    final_tfsa_func = optimize.subscribe_optimized_scalar(
        "final_tfsa", 0, 1, final_tfsa_guess
    )
    initial_equalize_income_weighting_func = optimize.subscribe_optimized_scalar(
        "initial_equalize_income_weighting",
        0,
        1,
        initial_equalize_income_weighting_guess,
    )
    final_equalize_income_weighting_func = optimize.subscribe_optimized_scalar(
        "final_equalize_income_weighting", 0, 1, final_equalize_income_weighting_guess
    )
    rrsp_adjustment_func = optimize.subscribe_optimized_scalar(
        "rrsp_adjustment", -1, 1, rrsp_adjustment_guess
    )

    return _bad_seed_raw(
        partner1_salary_compound_rate,
        partner1_salary_plateau,
        partner2_salary_compound_rate,
        partner2_salary_plateau,
        initial_year,
        increase_savings_weight,
        initial_tfsa_func,
        final_tfsa_func,
        initial_equalize_income_weighting_func,
        final_equalize_income_weighting_func,
        partner1_year_of_retirement,
        partner2_year_of_retirement,
        final_year,
        rrsp_adjustment_func,
        rrsp_interest_rate,
        tfsa_interest_rate,
    )
