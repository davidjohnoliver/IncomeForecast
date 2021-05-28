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

        # Assume no current-year dependencies
        salary_rule,
        #Depends on deltas.gross_salary (ie salary_rule)
        natural_rules.apply_tax,

        # May depend on salary and tax
        spending_rule,

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

def get_couple_ruleset(partner1_salary_rule, partner2_salary_rule, spending_rule, savings_rule, rrsp_interest_rate: float, tfsa_interest_rate: float):
    def ruleset(current_year : int, is_partner1_retired : bool, is_partner2_retired : bool):
        for i in range(1, 3):
            # These rules don't have dependencies and apply both pre- and post-retirement
            # (Tax 'refund' can have either sign and is actually a payment when deducting from the RRSP)
            yield model.get_couple_rule_from_single_rule(natural_rules.apply_tax_refund, i)
            yield model.get_couple_rule_from_single_rule(natural_rules.get_calculate_investment_interest(rrsp_interest_rate, tfsa_interest_rate), i)
        
        # Those who are working earn income and pay tax
        if (not is_partner1_retired):
            yield model.get_couple_rule_from_single_rule(partner1_salary_rule, 1)
            yield model.get_couple_rule_from_single_rule(natural_rules.apply_tax, 1)
        if (not is_partner2_retired):
            yield model.get_couple_rule_from_single_rule(partner2_salary_rule, 2)
            yield model.get_couple_rule_from_single_rule(natural_rules.apply_tax, 2)
        

        yield spending_rule
        yield savings_rule
    
    return ruleset