import model
from typing import Callable

def get_simple_linear(initial_rrsp: float, final_rrsp: float, initial_year: int, career_length_yrs: int):
    """
    Sets the split between RRSP and TFSA as a linear function of time.

    s[y] = a + b*(y - y_0), where s = RRSP allotment (normalized), a = initial_rrsp (normalized value), 
                b = (final_rrsp - initial_rrsp) / career_length_yrs, y_0 = initial_year, y = current year
    """
    return get_simple_linear_func(lambda: initial_rrsp, lambda: final_rrsp, initial_year, career_length_yrs, None)


def get_simple_linear_func(initial_rrsp_func: Callable[[], float], final_rrsp_func: Callable[[], float], initial_year: int, career_length_yrs: int, fail_func: Callable[[], None]):
    """
    Sets the split between RRSP and TFSA as a linear function of time. Takes generator functions for initial_rrsp and final_rrsp to facilitate optimization.

    s[y] = a + b*(y - y_0), where s = RRSP allotment (normalized), initial_rrsp = initial_rrsp_func(), final_rrsp = final_rrsp_func(),
        a = initial_rrsp (normalized value), b = (final_rrsp - initial_rrsp) / career_length_yrs, y_0 = initial_year, y = current year
    """

    def simple_linear(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        initial_rrsp = initial_rrsp_func()
        final_rrsp = final_rrsp_func()

        if not (0 <= initial_rrsp <= 1):
            if fail_func != None:
                fail_func("savings_rules.simple_linear: initial_rrsp must be between 0 and 1")
            else:
                raise ValueError("initial_rrsp must be between 0 and 1")

        if not (0 <= final_rrsp <= 1):
            if fail_func != None:
                fail_func("savings_rules.simple_linear: final_rrsp must be between 0 and 1")
            else:
                raise ValueError("final_rrsp must be between 0 and 1")

        slope = (final_rrsp - initial_rrsp) / career_length_yrs

        years_elapsed = deltas.year - initial_year

        if not (0 <= years_elapsed <= career_length_yrs):
            raise ValueError(f"{deltas.year} lies outside the allowed range of years for the rule (initial year={initial_year}, career length={career_length_yrs})")

        rrsp_norm = initial_rrsp + slope * years_elapsed        
        is_in_bounds = 0 <= rrsp_norm <= 1
        if fail_func != None and not is_in_bounds:
            fail_func("savings_rules.simple_linear: interpolated RRSP must be between 0 and 1")
        else:
            assert is_in_bounds
        tfsa_norm = 1 - rrsp_norm

        output = deltas.update_rrsp(deltas.undifferentiated_savings * rrsp_norm)
        output = output.update_tfsa(deltas.undifferentiated_savings * tfsa_norm)

        return output
    
    return simple_linear

def get_simple_retirement_deduction(retirement_year: int, year_of_death: int):
    """
    Deduct from savings to cover retirement income. The split between RRSP and TFSA is made by a simple heuristic which tries to keep a 
    constant level of RRSP withdrawals, to minimize marginal tax.
    """

    def simple_retirement_deduction(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        years_elapsed = deltas.year - retirement_year
        years_remaining = year_of_death - deltas.year

        if (years_elapsed < 0 or deltas.year > year_of_death):
            raise ValueError(f"{deltas.year} lies outside the allowed range of years for the rule (initial year={retirement_year}, final year={year_of_death})")

        #
        spending = -deltas.undifferentiated_savings # We expect undifferentiated_savings to be a negative value, with contributions from
            # spending (retirement income) + tax owed on last year's RRSP withdrawal
        remaining_rrsp = previous_funds.rrsp_savings
        rrsp_allotment = remaining_rrsp / (years_remaining + 1) # Try to distribute RRSP withdrawals evenly to minimize marginal tax
        rrsp_withdrawal = max(min(spending, rrsp_allotment), 0) # Don't let the RRSP go below 0. This is mainly to try to cut down on weird edge 
            # cases; if final savings is below 0 for any given run we don't care that much, the outer simulation will simply discard that run.
        tfsa_withdrawal = spending - rrsp_withdrawal

        output = deltas.update_rrsp(-rrsp_withdrawal)
        output = output.update_tfsa(-tfsa_withdrawal)

        return output
    
    return simple_retirement_deduction

def get__linear_retirement_deduction_func(initial_rrsp_func: Callable[[], float], final_rrsp_func: Callable[[], float], initial_year: int, retirement_length_yrs: int, fail_func: Callable[[], None]):
    """
    Deduct from savings to cover retirement income. The split between RRSP and TFSA is made as a linear function of time. Takes generator 
    functions for initial_rrsp and final_rrsp to facilitate optimization.
    """
    inner_rule = get_simple_linear_func(initial_rrsp_func, final_rrsp_func, initial_year, retirement_length_yrs, fail_func)

    def checked_rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        output = inner_rule(deltas, previous_funds, previous_deltas)
        if (previous_funds.rrsp_savings + deltas.rrsp < 0):
            # 
            fail_func("savings_rules.linear_retirement_deduction: RRSP must not go below 0")
        return output
    
    return checked_rule

def get_adjusted_heuristic_retirement_deduction(retirement_year: int, year_of_death: int, rrsp_adjustment_func: Callable[[], float]):
    """
    Deduct from savings to cover retirement income. The split between RRSP and TFSA is made by a simple heuristic which tries to keep a 
    constant level of RRSP withdrawals, to minimize marginal tax, adjusted by an optimizable constant proportional offset.
    """

    def simple_retirement_deduction(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        years_elapsed = deltas.year - retirement_year
        years_remaining = year_of_death - deltas.year

        if (years_elapsed < 0 or deltas.year > year_of_death):
            raise ValueError(f"{deltas.year} lies outside the allowed range of years for the rule (initial year={retirement_year}, final year={year_of_death})")

        #
        spending = -deltas.undifferentiated_savings # We expect undifferentiated_savings to be a negative value, with contributions from
            # spending (retirement income) + tax owed on last year's RRSP withdrawal
        remaining_rrsp = previous_funds.rrsp_savings
        rrsp_allotment = remaining_rrsp / (years_remaining + 1) # Try to distribute RRSP withdrawals evenly to minimize marginal tax

        rrsp_proportional_adjustment = rrsp_adjustment_func() * spending

        rrsp_allotment += rrsp_proportional_adjustment # Apply the adjustment, we clamp to spending in the next line

        rrsp_withdrawal = max(min(spending, rrsp_allotment), 0) # Don't let the RRSP go below 0. This is mainly to try to cut down on weird edge 
            # cases; if final savings is below 0 for any given run we don't care that much, the outer simulation will simply discard that run.
        tfsa_withdrawal = spending - rrsp_withdrawal

        output = deltas.update_rrsp(-rrsp_withdrawal)
        output = output.update_tfsa(-tfsa_withdrawal)

        return output
    
    return simple_retirement_deduction
