"""
Covers 'natural' update rules, rules that are set by law, economics and/or mathematics, as opposed to rules that articulate the assumptions of the forecasting model.
"""

import model
import tax
import math_utils


def apply_tax(
    deltas: model.deltas_state,
    previous_funds: model.funds_state,
    previous_deltas: model.deltas_state,
):
    """Set income tax owed, *ignoring* RRSP contributions (since savings can only be calculated after the tax has been determined), but including benefits and income on unregistered investments."""
    income_tax = tax.get_income_tax(
        deltas.gross_salary + deltas.benefits + deltas.unregistered_interest
    )
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
        return deltas.update_tfsa_available_room(yearly_increase)

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
        return deltas.update_rrsp_available_room(
            min(
                # RRSP limit is calculated from 'earned income' which includes salary, bonuses etc, but not investment interest, dividends, other 'passive income'
                income_fraction * previous_deltas.gross_salary,
                annual_limit,
            )
        )

    return apply_update


def get_quebec_pension_plan(
    maximum_pensionable_earnings: float,
    pension_contribution: float,
    current_monthly_pension_at_60: float,
    projected_monthly_pension_at_60: float,
    current_monthly_pension_at_65: float,
    projected_monthly_pension_at_65: float,
    initial_year: int,
    current_age: int,
    retirement_age: int,
    pension_start_age: int,
):
    """
    Returns a rule which applies Quebec Pension Plan contributions before retirement and benefits once the pension has started.

    The algorithm for determining benefits is as follows:
 - lerp between current pension (ie pension if retiring right now) and projected pension (ie pension if retiring at pension start age) to get actualPensionAt60 and actualPensionAt65, based on retirementAge
 - lerp between actualPensionAt60 and actualPensionAt65 to get actualPension, based on pensionStartAge
    """

    def get_projection_fraction(projected_age: int):
        years_to_projected_age = projected_age - current_age
        if years_to_projected_age <= 0:
            return 1
        return math_utils.clamp(
            (retirement_age - current_age) / years_to_projected_age, 0, 1
        )

    actual_monthly_pension_at_60 = math_utils.lerp(
        current_monthly_pension_at_60,
        projected_monthly_pension_at_60,
        get_projection_fraction(60),
    )
    actual_monthly_pension_at_65 = math_utils.lerp(
        current_monthly_pension_at_65,
        projected_monthly_pension_at_65,
        get_projection_fraction(65),
    )
    pension_start_fraction = math_utils.clamp((pension_start_age - 60) / 5, 0, 1)
    actual_yearly_pension = (
        math_utils.lerp(
            actual_monthly_pension_at_60,
            actual_monthly_pension_at_65,
            pension_start_fraction,
        )
        * 12
    )
    yearly_contribution = maximum_pensionable_earnings * pension_contribution

    def apply_qpp(
        deltas: model.deltas_state,
        previous_funds: model.funds_state,
        previous_deltas: model.deltas_state,
    ):
        output_deltas = deltas
        age = current_age + deltas.year - initial_year
        if age < retirement_age:
            output_deltas = output_deltas.update_contributions(
                output_deltas.contributions + yearly_contribution
            )
        if age >= pension_start_age:
            output_deltas = output_deltas.update_benefits(
                output_deltas.benefits + actual_yearly_pension
            )
        return output_deltas

    return apply_qpp


def calculate_yearly_mortgage_payment(
    principal: float,
    amortization_length: int,
    interest: float,
) -> float:
    """
    Calculates the yearly mortgage payment based on Canadian standard: semi-annual compounding, monthly payments.
    """
    if amortization_length <= 0:
        raise ValueError("amortization_length must be greater than 0")

    # Constants for standard Canadian mortgage: semi-annual compounding, monthly payments
    compounding_frequency = 2
    payment_frequency = 12

    # Calculate effective periodic (monthly) rate
    # equivalent to Math.pow(1 + nominal_rate / compounding_freq, compounding_freq / payment_freq) - 1
    periodic_rate = (1 + interest / compounding_frequency) ** (
        compounding_frequency / payment_frequency
    ) - 1

    # Total number of payments
    total_payments = amortization_length * payment_frequency

    # Calculate periodic payment
    # equivalent to principal / ((1 - Math.pow(1 + periodic_rate, -1 * total_payments)) / periodic_rate)
    if periodic_rate > 0:
        monthly_payment = principal / (
            (1 - (1 + periodic_rate) ** (-total_payments)) / periodic_rate
        )
    else:
        monthly_payment = principal / total_payments

    return monthly_payment * payment_frequency


def get_mortgage_payment(
    remaining_principal: float,
    initial_remaining_amortization_length: int,
    mortgage_interest: float,
    initial_year: int,
):
    """
    Returns a rule which deducts mortgage repayments, over a period of amortization.

    This is currently geared towards a 'primary residence' scenario. Mortgage payments are treated as essentially disappearing into the ether, under the implicit assumption that it will be fully paid off at the end of the simulation and held as an asset.
    """

    yearly_payment = calculate_yearly_mortgage_payment(
        remaining_principal, initial_remaining_amortization_length, mortgage_interest
    )

    end_year = initial_year + initial_remaining_amortization_length

    def mortgage_payment(
        deltas: model.deltas_state,
        previous_funds: model.funds_state,
        previous_deltas: model.deltas_state,
    ):
        if deltas.year < end_year:
            output_deltas = deltas.update_debt_payments(
                deltas.debt_payments + yearly_payment
            )
            return output_deltas
        return deltas

    return mortgage_payment


def get_couple_mortgage_payment(
    remaining_principal: float,
    initial_remaining_amortization_length: int,
    mortgage_interest: float,
    initial_year: int,
):
    """
    Returns a couple rule which deducts mortgage repayments at the household level, over a period of amortization.
    """

    yearly_payment = calculate_yearly_mortgage_payment(
        remaining_principal, initial_remaining_amortization_length, mortgage_interest
    )

    end_year = initial_year + initial_remaining_amortization_length

    def mortgage_payment(
        deltas: model.couple_deltas_state,
        previous_funds: model.couple_funds_state,
        previous_deltas: model.couple_deltas_state,
    ):
        if deltas.year < end_year:
            output_deltas = deltas.update_household_debt_payments(
                deltas.household_debt_payments + yearly_payment
            )
            return output_deltas
        return deltas

    return mortgage_payment
