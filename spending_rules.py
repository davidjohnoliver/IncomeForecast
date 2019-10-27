"""
Rules describing the trajectory of spending over time.
"""

import model


def get_luxury_over_basic(base_spending: float, luxury_compound_rate: float):
    """
    Models expenditure as a compounding 'luxury' component added to a fixed 'basic needs' component.
    
    sp[y] = b + (1 + c)sp[y-1], where sp = spending, b = base_spending, c = luxury_compound_rate
    """

    def luxury_over_basic(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        previous_luxury = previous_deltas.spending - base_spending
        if (previous_luxury < 0):
                # Try to somehow handle spending below the 'basic level,' since the solver will try spendings from 0 upwards. Consumer code 
                # is responsible for warning the user if the actual solution returns a spending below the 'basic' level.
                new_spending = (1 + luxury_compound_rate) * previous_deltas.spending
                return deltas.update_spending(new_spending)
        
        new_luxury = (1 + luxury_compound_rate) * previous_luxury
        return deltas.update_spending(base_spending + new_luxury)

    return luxury_over_basic
