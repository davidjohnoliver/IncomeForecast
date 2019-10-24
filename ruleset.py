"""
Helper functions for building a ruleset.
"""

import natural_rules
import model

def get_career_rules(salary_rule, spending_rule, savings_rule, rrsp_interest_rate: float, tfsa_interest_rate: float):
    """
    Takes assumption-driven rules as input and returns a full career ruleset including 'natural' rules, correctly ordered.
    
    :param salary_rule: Rule setting the gross salary.
    :param spending_rule: Rule setting the amount of spending.
    :param savings_rule: Rule dividing the available savings between RRSP and TFSA.
    :param rrsp_interest_rate: Interest rate on the RRSP account.
    :type rrsp_interest_rate: float
    :param tfsa_interest_rate: Interest rate on the TFSA account.
    :type tfsa_interest_rate: float
    :return: A full career ruleset.
    """

    return [
        # No current-year dependencies
        natural_rules.apply_tax_refund,
        natural_rules.get_calculate_investment_interest(rrsp_interest_rate, tfsa_interest_rate),

        # We assume these have no current-year dependencies
        salary_rule,
        spending_rule,

        #Depends on deltas.gross_salary (ie salary_rule)
        natural_rules.apply_tax,

        # Depends on pretty much everything else
        savings_rule
    ]

def get_retirement_rules(retirement_income: float, savings_rule, rrsp_interest_rate: float, tfsa_interest_rate: float):
    """
    Returns a retirement ruleset including 'natural' rules, correctly ordered.
    
    :param retirement_income: Yearly 'income' or expenditure during retirement, assumed to be constant.
    :type retirement_income: float
    :param savings_rule: Rule governing the distribution of deductions between RRSP and TFSA accounts.
    :param rrsp_interest_rate: Interest rate on the RRSP account.
    :type rrsp_interest_rate: float
    :param tfsa_interest_rate: Interest rate on the TFSA account.
    :type tfsa_interest_rate: float
    :return: The retirement ruleset.
    """

    def retirement_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(retirement_income)
    
    return [
        retirement_spending, # Spend
        # Skip tax on employment salary since we're not employed
        natural_rules.apply_tax_refund, # Pay tax on previous year's RRSP deductions and investment interest
        savings_rule, # Deduct spending from RRSP/TFSA according to rule
        natural_rules.get_calculate_investment_interest(rrsp_interest_rate, tfsa_interest_rate) # Earn interest on remaining savings
    ]
    
#def get_retirement_rules_simple_linear_savings(retirement_income, )