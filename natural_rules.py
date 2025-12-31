"""
Covers 'natural' update rules, rules that are set by law, economics and/or mathematics, as opposed to rules that articulate the assumptions of the forecasting model.
"""

import model
import tax


def apply_tax(
    deltas: model.deltas_state,
    previous_funds: model.funds_state,
    previous_deltas: model.deltas_state,
):
    """Set income tax owed, *ignoring* RRSP contributions (since savings can only be calculated after the tax has been determined), but including income on unregistered investments."""
    income_tax = tax.get_income_tax(deltas.gross_salary + deltas.unregistered_interest)
    return deltas.update_tax(income_tax)


def apply_tax_refund(
    deltas: model.deltas_state,
    previous_funds: model.funds_state,
    previous_deltas: model.deltas_state,
):
    """
    Calculates and sets the tax refund/extra-owed for the current year, based on the overpayment (because of RRSP contributions) or underpayment (because
    of RRSP deductions) in the previous year.
    """
    post_rrsp_tax = tax.get_income_tax(previous_deltas.taxable_income)
    diff = previous_deltas.tax - post_rrsp_tax
    if (
        previous_deltas.rrsp > 0
        and previous_deltas.tax > 0
        and previous_deltas.rrsp_interest < previous_deltas.rrsp
    ):
        assert diff > 0

    return deltas.update_tax_refund(diff)


def get_calculate_investment_interest(
    rrsp_interest_rate: float,
    tfsa_interest_rate: float,
    unregistered_interest_rate: float,
):
    """
    Gets a rule which applies compound interest to accumulate savings, according to the supplied interest rates (fractions).
    """

    def calculate_investment_interest(
        deltas: model.deltas_state,
        previous_funds: model.funds_state,
        previous_deltas: model.deltas_state,
    ):
        output = deltas.update_rrsp_interest(
            previous_funds.rrsp_savings * rrsp_interest_rate
        )
        output = output.update_tfsa_interest(
            previous_funds.tfsa_savings * tfsa_interest_rate
        )
        output = output.update_unregistered_interest(
            previous_funds.unregistered_savings * unregistered_interest_rate
        )

        return output

    return calculate_investment_interest


def increase_tfsa_limit(yearly_increase: float):
    """
    Returns a rule which sets the TFSA contribution room delta for the year to the supplied yearly_increase.
    """

    def apply_increase(
        deltas: model.deltas_state,
        previous_funds: model.funds_state,
        previous_deltas: model.deltas_state,
    ):
        return deltas.update_tfsa_limit(yearly_increase)

    return apply_increase


def get_update_rrsp_limit(income_fraction: float, annual_limit: float):
    """
    Returns a rule which sets the RRSP contribution room delta for the year to the lesser of
    income_fraction * last year's gross income and annual_limit.
    """

    def apply_update(
        deltas: model.deltas_state,
        previous_funds: model.funds_state,
        previous_deltas: model.deltas_state,
    ):
        return deltas.update_rrsp_limit(
            min(
                # RRSP limit is calculated from 'earned income' which includes salary, bonuses etc, but not investment interest, dividends, other 'passive income'
                income_fraction * previous_deltas.gross_salary,
                annual_limit,
            )
        )

    return apply_update
