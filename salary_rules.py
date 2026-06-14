"""
Rules describing the increase of salary over time.
"""

import model

def get_compound_plateau(compound_rate: float, plateau: float):
    """
    Models salary compounding each year, until it plateaus at a defined maximum.

    s[y] = min[p, (1 + c)s[y-1]] where s = salary, y = year, p = plateau value and c = compound_rate
    """

    def compound_plateau(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        compounded_salary = (1 + compound_rate) * previous_deltas.gross_salary
        new_salary = min(plateau, compounded_salary)
        return deltas.update_gross_salary(new_salary)

    return compound_plateau


def get_rrsp_matching(matching_cap_fraction: float):
    """
    Models employer RRSP matching, where the employer matches the employee's RRSP contribution dollar-for-dollar, up to a
    cap expressed as a fraction of gross salary.

    m = min[r, f*s], further capped so that the total contribution doesn't exceed the available RRSP room, where
    m = employer match, r = employee RRSP contribution, f = matching_cap_fraction and s = gross_salary.

    This rule reads the employee's contribution from deltas.rrsp, so it must run after the rule that sets it (eg the
    savings rule). The RRSP room limit is taken from the funds state updated with the current deltas, consistent with
    couple_savings_rules.get_split_by_investment_then_partner_with_limits (it accounts for carried-forward room, this
    year's new room, and the employee's own contribution already applied).

    The match is added both to the RRSP contribution (it's deposited in the RRSP) and to benefits (it's a taxable benefit).
    """

    def rrsp_matching(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        cap = matching_cap_fraction * deltas.gross_salary
        current_funds = model.get_updated_funds_from_deltas(previous_funds, deltas)
        remaining_rrsp_room = current_funds.rrsp_available_room
        match = max(0, min(deltas.rrsp, cap, remaining_rrsp_room))

        output = deltas.update_rrsp(deltas.rrsp + match)
        output = output.update_benefits(output.benefits + match)
        return output

    return rrsp_matching