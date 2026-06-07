import ruleset
import salary_rules
import couple_savings_rules
import couple_spending_rules
import natural_rules
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
        partner1_salary_rule=salary_rules.get_compound_plateau(
            partner1_salary_compound_rate, partner1_salary_plateau
        ),
        partner2_salary_rule=salary_rules.get_compound_plateau(
            partner2_salary_compound_rate, partner2_salary_plateau
        ),
        spending_rule=couple_spending_rules.get_luxury_over_basic(
            base_spending, spending_luxury_compound_rate
        ),
        savings_rule=couple_savings_rules.get_equalizing_rrsp_only_split(),
        rrsp_interest_rate=rrsp_interest_rate,
        tfsa_interest_rate=tfsa_interest_rate,
        unregistered_interest_rate=0,  # Unregistered interest not supported
        tfsa_yearly_increase=0.0, # TFSA and RRSP limits not supported
        rrsp_income_fraction=0.0,
        rrsp_annual_limit=0.0,
        partner1_pretax_rules=[],
        partner2_pretax_rules=[],
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
        partner1_salary_rule=salary_rules.get_compound_plateau(
            partner1_salary_compound_rate, partner1_salary_plateau
        ),
        partner2_salary_rule=salary_rules.get_compound_plateau(
            partner2_salary_compound_rate, partner2_salary_plateau
        ),
        spending_rule=couple_spending_rules.get_increasing_savings_increasing_spending(
            initial_year, increase_savings_weight
        ),
        savings_rule=couple_savings_rules.get_split_by_investment_then_partner(
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
        rrsp_interest_rate=rrsp_interest_rate,
        tfsa_interest_rate=tfsa_interest_rate,
        unregistered_interest_rate=0,  # Unregistered interest not supported
        tfsa_yearly_increase=0.0, # TFSA and RRSP limits not supported
        rrsp_income_fraction=0.0,
        rrsp_annual_limit=0.0,
        partner1_pretax_rules=[],
        partner2_pretax_rules=[],
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


def _charlie_raw(
    partner1_salary_compound_rate: float,
    partner1_salary_plateau: float,
    partner2_salary_compound_rate: float,
    partner2_salary_plateau: float,
    initial_year: int,
    increase_savings_weight: float,
    initial_non_rrsp_func: Callable[[], float],
    final_non_rrsp_func: Callable[[], float],
    initial_equalize_income_weighting_func: Callable[[], float],
    final_equalize_income_weighting_func: Callable[[], float],
    partner1_year_of_retirement: int,
    partner2_year_of_retirement: int,
    final_year: int,
    rrsp_adjustment_func: Callable[[], float],
    rrsp_interest_rate: float,
    tfsa_interest_rate: float,
    unregistered_interest_rate: float,
    tfsa_yearly_increase: float,
    rrsp_income_fraction: float,
    rrsp_annual_limit: float,
    mortgage_principal: float,
    mortgage_amortization: int,
    mortgage_interest: float,
    qpp_maximum_pensionable_earnings: float,
    qpp_pension_contribution: float,
    partner1_current_monthly_pension_at_60: float,
    partner1_projected_monthly_pension_at_60: float,
    partner1_current_monthly_pension_at_65: float,
    partner1_projected_monthly_pension_at_65: float,
    partner1_retirement_age: int,
    partner1_pension_start_age: int,
    partner2_current_monthly_pension_at_60: float,
    partner2_projected_monthly_pension_at_60: float,
    partner2_current_monthly_pension_at_65: float,
    partner2_projected_monthly_pension_at_65: float,
    partner2_retirement_age: int,
    partner2_pension_start_age: int,
):

    mortgage_payment_rule = None
    if mortgage_principal > 0 and mortgage_amortization > 0:
        mortgage_payment_rule = natural_rules.get_couple_mortgage_payment(
            remaining_principal=mortgage_principal,
            initial_remaining_amortization_length=mortgage_amortization,
            mortgage_interest=mortgage_interest,
            initial_year=initial_year,
        )

    partner1_qpp_rule = natural_rules.get_quebec_pension_plan(
        maximum_pensionable_earnings=qpp_maximum_pensionable_earnings,
        pension_contribution=qpp_pension_contribution,
        current_monthly_pension_at_60=partner1_current_monthly_pension_at_60,
        projected_monthly_pension_at_60=partner1_projected_monthly_pension_at_60,
        current_monthly_pension_at_65=partner1_current_monthly_pension_at_65,
        projected_monthly_pension_at_65=partner1_projected_monthly_pension_at_65,
        initial_year=initial_year,
        current_age=partner1_retirement_age
        - (partner1_year_of_retirement - initial_year),
        retirement_age=partner1_retirement_age,
        pension_start_age=partner1_pension_start_age,
    )
    partner2_qpp_rule = natural_rules.get_quebec_pension_plan(
        maximum_pensionable_earnings=qpp_maximum_pensionable_earnings,
        pension_contribution=qpp_pension_contribution,
        current_monthly_pension_at_60=partner2_current_monthly_pension_at_60,
        projected_monthly_pension_at_60=partner2_projected_monthly_pension_at_60,
        current_monthly_pension_at_65=partner2_current_monthly_pension_at_65,
        projected_monthly_pension_at_65=partner2_projected_monthly_pension_at_65,
        initial_year=initial_year,
        current_age=partner2_retirement_age
        - (partner2_year_of_retirement - initial_year),
        retirement_age=partner2_retirement_age,
        pension_start_age=partner2_pension_start_age,
    )

    ruleset_func = ruleset.get_couple_ruleset(
        partner1_salary_rule=salary_rules.get_compound_plateau(
            partner1_salary_compound_rate, partner1_salary_plateau
        ),
        partner2_salary_rule=salary_rules.get_compound_plateau(
            partner2_salary_compound_rate, partner2_salary_plateau
        ),
        spending_rule=couple_spending_rules.get_increasing_savings_increasing_spending(
            initial_year, increase_savings_weight
        ),
        savings_rule=couple_savings_rules.get_split_by_investment_then_partner_with_limits(
            initial_non_rrsp_func,
            final_non_rrsp_func,
            initial_equalize_income_weighting_func,
            final_equalize_income_weighting_func,
            partner1_year_of_retirement,
            partner2_year_of_retirement,
            initial_year,
            final_year,
            rrsp_adjustment_func,
        ),
        rrsp_interest_rate=rrsp_interest_rate,
        tfsa_interest_rate=tfsa_interest_rate,
        unregistered_interest_rate=unregistered_interest_rate,
        tfsa_yearly_increase=tfsa_yearly_increase,
        rrsp_income_fraction=rrsp_income_fraction,
        rrsp_annual_limit=rrsp_annual_limit,
        partner1_pretax_rules=[partner1_qpp_rule],
        partner2_pretax_rules=[partner2_qpp_rule],
        mortgage_payment_rule=mortgage_payment_rule,
    )

    return ruleset_func


def charlie(
    partner1_salary_compound_rate: float,
    partner1_salary_plateau: float,
    partner2_salary_compound_rate: float,
    partner2_salary_plateau: float,
    initial_year: int,
    increase_savings_weight: float,
    initial_non_rrsp_guess: float,
    final_non_rrsp_guess: float,
    initial_equalize_income_weighting_guess: float,
    final_equalize_income_weighting_guess: float,
    partner1_year_of_retirement: int,
    partner2_year_of_retirement: int,
    final_year: int,
    rrsp_adjustment_guess: float,
    rrsp_interest_rate: float,
    tfsa_interest_rate: float,
    unregistered_interest_rate: float,
    tfsa_yearly_increase: float,
    rrsp_income_fraction: float,
    rrsp_annual_limit: float,
    optimize: solve.Optimizing_Solver,
    mortgage_principal: float,
    mortgage_amortization: int,
    mortgage_interest: float,
    qpp_maximum_pensionable_earnings: float,
    qpp_pension_contribution: float,
    partner1_current_monthly_pension_at_60: float,
    partner1_projected_monthly_pension_at_60: float,
    partner1_current_monthly_pension_at_65: float,
    partner1_projected_monthly_pension_at_65: float,
    partner1_retirement_age: int,
    partner1_pension_start_age: int,
    partner2_current_monthly_pension_at_60: float,
    partner2_projected_monthly_pension_at_60: float,
    partner2_current_monthly_pension_at_65: float,
    partner2_projected_monthly_pension_at_65: float,
    partner2_retirement_age: int,
    partner2_pension_start_age: int,
):
    """
    A dual-income ruleset which uses the increasing_savings_increasing_spending rule for spending vs. saving, and the split_by_investment_then_partner_with_limits rule for savings allocations
    """

    initial_non_rrsp_func = optimize.subscribe_optimized_scalar(
        "initial_non_rrsp", 0, 1, initial_non_rrsp_guess
    )
    final_non_rrsp_func = optimize.subscribe_optimized_scalar(
        "final_non_rrsp", 0, 1, final_non_rrsp_guess
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

    return _charlie_raw(
        partner1_salary_compound_rate=partner1_salary_compound_rate,
        partner1_salary_plateau=partner1_salary_plateau,
        partner2_salary_compound_rate=partner2_salary_compound_rate,
        partner2_salary_plateau=partner2_salary_plateau,
        initial_year=initial_year,
        increase_savings_weight=increase_savings_weight,
        initial_non_rrsp_func=initial_non_rrsp_func,
        final_non_rrsp_func=final_non_rrsp_func,
        initial_equalize_income_weighting_func=initial_equalize_income_weighting_func,
        final_equalize_income_weighting_func=final_equalize_income_weighting_func,
        partner1_year_of_retirement=partner1_year_of_retirement,
        partner2_year_of_retirement=partner2_year_of_retirement,
        final_year=final_year,
        rrsp_adjustment_func=rrsp_adjustment_func,
        rrsp_interest_rate=rrsp_interest_rate,
        tfsa_interest_rate=tfsa_interest_rate,
        unregistered_interest_rate=unregistered_interest_rate,
        tfsa_yearly_increase=tfsa_yearly_increase,
        rrsp_income_fraction=rrsp_income_fraction,
        rrsp_annual_limit=rrsp_annual_limit,
        mortgage_principal=mortgage_principal,
        mortgage_amortization=mortgage_amortization,
        mortgage_interest=mortgage_interest,
        qpp_maximum_pensionable_earnings=qpp_maximum_pensionable_earnings,
        qpp_pension_contribution=qpp_pension_contribution,
        partner1_current_monthly_pension_at_60=partner1_current_monthly_pension_at_60,
        partner1_projected_monthly_pension_at_60=partner1_projected_monthly_pension_at_60,
        partner1_current_monthly_pension_at_65=partner1_current_monthly_pension_at_65,
        partner1_projected_monthly_pension_at_65=partner1_projected_monthly_pension_at_65,
        partner1_retirement_age=partner1_retirement_age,
        partner1_pension_start_age=partner1_pension_start_age,
        partner2_current_monthly_pension_at_60=partner2_current_monthly_pension_at_60,
        partner2_projected_monthly_pension_at_60=partner2_projected_monthly_pension_at_60,
        partner2_current_monthly_pension_at_65=partner2_current_monthly_pension_at_65,
        partner2_projected_monthly_pension_at_65=partner2_projected_monthly_pension_at_65,
        partner2_retirement_age=partner2_retirement_age,
        partner2_pension_start_age=partner2_pension_start_age,
    )
