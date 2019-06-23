"""
Covers 'natural' update rules, rules that are set by law, economics and/or mathematics, as opposed to rules that articulate the assumptions of the forecasting model.
"""

import model
import tax

def apply_tax(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
    """Set income tax owed, calculated from the taxable income. This should only be called after salary has been set and rrsp contribution has been set."""
    income_tax = tax.get_income_tax(deltas.taxable_income)
    return deltas.update_tax(income_tax)