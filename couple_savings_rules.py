import model


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
