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