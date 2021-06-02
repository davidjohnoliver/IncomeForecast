import model
from typing import Callable
from typing import List
from math_utils import lerp
from math_utils import clamp
from loop_utils import Loop_Protection


def _get_higher_and_lower_partners(deltas: model.couple_deltas_state):
    if deltas.partner2_deltas.gross_salary > deltas.partner1_deltas.gross_salary:
        return (deltas.partner2_deltas, deltas.partner1_deltas)
    else:
        return (deltas.partner1_deltas, deltas.partner2_deltas)


def _update_higher_and_lower(
    deltas: model.couple_deltas_state,
    higher_delta: model.deltas_state,
    lower_delta: model.deltas_state,
):
    if deltas.partner2_deltas.gross_salary > deltas.partner1_deltas.gross_salary:
        return deltas.update_partner2_deltas(higher_delta).update_partner1_deltas(
            lower_delta
        )
    else:
        return deltas.update_partner1_deltas(higher_delta).update_partner2_deltas(
            lower_delta
        )


def _get_rrsp_withdrawal_allotment(
    funds: model.funds_state, years_remaining: int, adjustment: float, spending: float
):
    allotment = funds.rrsp_savings / (years_remaining + 1)
    allotment += adjustment * spending
    allotment = clamp(allotment, 0, min(spending / 2, funds.rrsp_savings))
    return allotment


def _get_tfsa_withdrawal_allotment(funds: model.funds_state, remaining_spending: float):
    return clamp(remaining_spending / 2, 0, max(funds.tfsa_savings, 0))


def _adjust_values_to_produce_sum(values_and_limits, target_sum: float):
    """Adjust values within respective limits so that they add up to target_sum"""
    TOLERANCE = 1e-6

    def values_sum():
        return sum([x[0] for x in values_and_limits])

    if values_sum() > target_sum + TOLERANCE:
        raise ValueError

    lp = Loop_Protection()
    while (shortfall := target_sum - values_sum()) > TOLERANCE:
        lp.iterate()
        increase_rooms = [x[1] - x[0] for x in values_and_limits]
        incrs_with_room = [x for x in increase_rooms if x > TOLERANCE]
        if len(incrs_with_room) == 0:
            # There's no valid solution. Increase the last value past its limit to satisfy the sum.
            i_last = len(values_and_limits) - 1
            current_last = values_and_limits[i_last]
            values_and_limits[i_last] = (current_last[0] + shortfall, current_last[1])
            break
        valid_incr = min(incrs_with_room)
        valid_incr = min(
            valid_incr, shortfall / len(incrs_with_room)
        )  # Ensure not to increment beyond target sum
        values_and_limits = [
            (min(x[0] + valid_incr, x[1]), x[1]) for x in values_and_limits
        ]  # Increase each value that has room to increase

    return values_and_limits


def get_equalizing_rrsp_only_split():
    """
    Get a saving allocation rule that puts all money into RRSPs and tries to equalize the taxable income of each partner as much as possible. When the couple is retired, it withdraws from RRSPs equally as much as possible.

    This rule is relatively simple and therefore useful for testing that other components are working as expected.

    Examples:
    $14k to be saved. Partner 1 is earning $60k (pre-tax), Partner 2 is earning $64k. Partner 1 will save $5k in their RRSP and Partner 2 will save $9k in their RRSP, for equal taxable incomes of $55k.

    $12k to be saved. Partner 1 is earning $72k and Partner 2 is earning $57k. Partner 1 will save the entire $12k in their RRSP, for taxable incomes of $60k and $57k respectively.
    """

    def equalizing_rrsp_only_split(
        deltas: model.couple_deltas_state,
        previous_funds: model.couple_funds_state,
        previous_deltas: model.couple_deltas_state,
    ):
        raw_savings = deltas.household_undifferentiated_savings
        if (
            raw_savings >= 0
        ):  # The couple is 'functionally working', ie their salaried net income exceeds their spending (though one of the partners may have retired)
            higher, lower = _get_higher_and_lower_partners(deltas)
            salary_diff = higher.gross_salary - lower.gross_salary
            if salary_diff >= raw_savings:
                # In the simplest case, the higher earner's extra earnings are sufficient to cover the entire amount to be saved.
                higher = higher.update_rrsp(raw_savings)
            else:
                excess_split = (raw_savings - salary_diff) / 2
                higher = higher.update_rrsp(salary_diff + excess_split)
                lower = lower.update_rrsp(excess_split)

            return _update_higher_and_lower(deltas, higher, lower)
        else:  # raw_savings < 0, The couple is 'functionally retired', ie their spending exceeds their salaried net income (though one of the partners may still be working)
            partner1_contribution = partner2_contribution = raw_savings / 2
            if (
                partner1_shortfall := max(
                    previous_funds.partner1_funds.rrsp_savings + partner1_contribution,
                    raw_savings / 2,
                )
            ) < 0:
                # If partner 1 would put their RRSP below 0, have partner 2 make up the difference
                partner2_contribution += partner1_shortfall
                partner1_contribution -= partner1_shortfall
            if (
                partner2_shortfall := max(
                    previous_funds.partner2_funds.rrsp_savings + partner2_contribution,
                    raw_savings / 2,
                )
            ) < 0:
                # If partner 2 would put their RRSP below 0, have partner 1 make up the difference. Note this may put partner 1's RRSP below 0; this is ok, the solver will ultimately discard this run.
                partner1_contribution += partner2_shortfall
                partner2_contribution -= partner2_shortfall

            return deltas.update_partner1_deltas(
                deltas.partner1_deltas.update_rrsp(partner1_contribution)
            ).update_partner2_deltas(
                deltas.partner2_deltas.update_rrsp(partner2_contribution)
            )

    return equalizing_rrsp_only_split


def get_split_by_investment_then_partner(
    initial_tfsa: Callable[[], float],
    final_tfsa: Callable[[], float],
    initial_equalize_income_weighting: Callable[[], float],
    final_equalize_income_weighting: Callable[[], float],
    partner1_year_of_retirement: int,
    partner2_year_of_retirement: int,
    initial_year: int,
    final_year: int,
    rrsp_adjustment_func: Callable[[], float],
):
    """
    Get a savings allocation rule that follows the strategy:
    . Is the couple 'functionally working' (ie their net income exceeds their spending)?
        Yes:
        1. Split savings between joint RRSP and joint TFSA, according to an optimizable, linearly time-varying weighting.
        2. For RRSP, linearly interpolate between two values: the RRSP contributions that would tend to equalize taxable
            incomes, and identical RRSP contributionsaccording to an optimizable, linearly time-varying weighting. (The
            intuition here is that there's a tension between minimizing marginal taxes while working, versus minimizing
            marginal taxes after retirement, with the latter presumably served by both partners having the same total RRSP.)
        3. Split TFSA 50:50. (The intuition is it doesn't matter much, since the program doesn't currently model contribution limits.)

        No, the couple is 'functionally retired':
        1. Get RRSP withdrawal for each partner by taking a year's worth of their remaining RRSP, adjusted by an optimizable correction
            factor, and clamped to be less than their remaining RRSP, less than combined spending / 2, and greater than 0.
        2. Get TFSA withdrawal for each partner as half of remaining spending to cover, clamped to be within their remaining total TFSA.
        3. Adjust each withdrawal upwards equally within the limits of remaining funds to cover target spending. If all funds are depleted,
            overdraw from partner 2's TFSA. (This is only of internal technical interest, since the simulation should discard runs where
            this occurs.)

        Since this rule switches from 'both partners contributing to savings' to 'both partners withdrawing from savings' with no mixed mode,
        it's most appropriate for cases where both partners retire fairly closely together. It may give poor results if one partner retires much later
        than the other.
    """

    estimated_year_of_functional_retirement = (
        partner1_year_of_retirement + partner2_year_of_retirement
    ) / 2  # This is not very robust, but we are not trying here very seriously to support widely divergent years of retirement

    def split_by_investment_then_partner(
        deltas: model.couple_deltas_state,
        previous_funds: model.couple_funds_state,
        previous_deltas: model.couple_deltas_state,
    ):
        raw_savings = deltas.household_undifferentiated_savings
        if (
            raw_savings >= 0
        ):  # The couple is 'functionally working', ie their salaried net income exceeds their spending (though one of the partners may have retired)
            t = (deltas.year - initial_year) / (
                estimated_year_of_functional_retirement - initial_year
            )
            tfsa_norm = lerp(initial_tfsa(), final_tfsa(), t)
            household_tfsa = tfsa_norm * raw_savings

            household_rrsp = raw_savings - household_tfsa
            equalize_income_weighting = lerp(
                initial_equalize_income_weighting(),
                final_equalize_income_weighting(),
                t,
            )
            higher, lower = _get_higher_and_lower_partners(deltas)
            salary_diff = higher.gross_salary - lower.gross_salary
            rrsp_equalize_income = (
                household_rrsp
                if salary_diff > household_rrsp
                else salary_diff + (household_rrsp - salary_diff) / 2
            )
            rrsp_equal_contribution = household_rrsp / 2
            rrsp_higher = lerp(
                rrsp_equal_contribution, rrsp_equalize_income, equalize_income_weighting
            )
            rrsp_lower = household_rrsp - rrsp_higher
            higher = higher.update_tfsa(household_tfsa / 2).update_rrsp(rrsp_higher)
            lower = lower.update_tfsa(household_tfsa / 2).update_rrsp(rrsp_lower)
            return _update_higher_and_lower(deltas, higher, lower)

        else:  # raw_savings < 0, The couple is 'functionally retired', ie their spending exceeds their salaried net income (though one of the partners may still be working)
            rrsp_adjustment = rrsp_adjustment_func()
            years_remaining = final_year - deltas.year

            spending = (
                -raw_savings
            )  # Flip the sign to deal with positive numbers and save brain cells
            rrsp_partner1 = _get_rrsp_withdrawal_allotment(
                previous_funds.partner1_funds,
                years_remaining,
                rrsp_adjustment,
                spending,
            )
            rrsp_partner2 = _get_rrsp_withdrawal_allotment(
                previous_funds.partner2_funds,
                years_remaining,
                rrsp_adjustment,
                spending,
            )

            remaining_spending = spending - rrsp_partner1 - rrsp_partner2
            tfsa_partner1 = _get_tfsa_withdrawal_allotment(
                previous_funds.partner1_funds, remaining_spending
            )
            tfsa_partner2 = _get_tfsa_withdrawal_allotment(
                previous_funds.partner2_funds, remaining_spending
            )

            allotments_and_limits = [
                (rrsp_partner1, previous_funds.partner1_funds.rrsp_savings),
                (rrsp_partner2, previous_funds.partner2_funds.rrsp_savings),
                (tfsa_partner1, previous_funds.partner1_funds.tfsa_savings),
                (tfsa_partner2, previous_funds.partner2_funds.tfsa_savings),
            ]
            allotments_and_limits = _adjust_values_to_produce_sum(
                allotments_and_limits, spending
            )
            allotments = [-x[0] for x in allotments_and_limits]  # Flip the sign back

            partner1_deltas = deltas.partner1_deltas.update_rrsp(
                allotments[0]
            ).update_tfsa(allotments[2])
            partner2_deltas = deltas.partner2_deltas.update_rrsp(
                allotments[1]
            ).update_tfsa(allotments[3])

            return deltas.update_partner1_deltas(
                partner1_deltas
            ).update_partner2_deltas(partner2_deltas)

    return split_by_investment_then_partner

