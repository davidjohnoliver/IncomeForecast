"""
Covers 'natural' update rules, rules that are set by law, economics and/or mathematics, as opposed to rules that articulate the assumptions of the forecasting model.
"""

import model
import tax

def apply_tax(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
    """Set income tax owed, *ignoring* RRSP contributions (since savings can only be calculated after the tax has been determined)."""
    income_tax = tax.get_income_tax(deltas.gross_salary)
    return deltas.update_tax(income_tax)

def apply_tax_refund(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
    """
    Calculates and sets the tax refund for the current year, based on the overpayment (because of RRSP contributions) in the previous year.
    """
    post_rrsp_tax = tax.get_income_tax(previous_deltas.taxable_income)
    diff = previous_deltas.tax - post_rrsp_tax
    if previous_deltas.rrsp > 0 and previous_deltas.tax > 0:
        assert diff > 0
        
    return deltas.update_tax_refund(diff)