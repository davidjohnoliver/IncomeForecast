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

def get_luxury_over_basic_capped(base_spending: float, luxury_compound_rate: float, cap_fractional: float):
    """
    Models expenditure as a compounding 'luxury' component added to a fixed 'basic needs' component. Caps spending at some fraction of net income. 
    
    sp[y] = min(b + (1 + c)sp[y-1], f * i), where sp = spending, b = base_spending, c = luxury_compound_rate, f = cap_fractional, i = deltas.total_net_income
    """

    def luxury_over_basic_capped(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        previous_luxury = previous_deltas.spending - base_spending
        if (previous_luxury < 0):
                # Try to somehow handle spending below the 'basic level,' since the solver will try spendings from 0 upwards. Consumer code 
                # is responsible for warning the user if the actual solution returns a spending below the 'basic' level.
                new_spending = (1 + luxury_compound_rate) * previous_deltas.spending
                return deltas.update_spending(new_spending)
        
        new_luxury = (1 + luxury_compound_rate) * previous_luxury
        cap = deltas.total_net_income * cap_fractional
        spending = min(cap, base_spending +  new_luxury)
        return deltas.update_spending(spending)

    return luxury_over_basic_capped

def get_increasing_savings_increasing_spending(initial_year : float, increase_savings_weight : float, should_clamp_absolute_spending : bool):
    """
    A somewhat complex spending rule which tries to enforce the following intuitively desirable traits:
        - savings, as a fraction of after-tax income, should only ever increase
        - spending, in absolute dollars, should only ever increase
    
    It also has the following mathematically useful characteristics:
        - if the initial savings is 0 (ie initial spending == initial after-tax income), then total career savings will be very close to 0
        - if the initial spending is 0, then total career spending will be very close to 0
    (These characteristics maximise the ability to find a solution for a given income function and savings target)

    It determines the spending per-year as follows:
        1. The spending that would maintain the same proportional savings is taken as a ceiling, call this sp_ceil
        2. The spending that would maintain the same absolute spending (ie the previous year's value) is taken as sp_floor
        3. Actual spending is sp = sp_ceil*(1 - increase_savings_weight) + sp_floor*increase_savings_weight.
            Hence if increase_savings_weight = 0.5, the average will be taken. If increase_savings_weight = 1, any increase in salary will be
            entirely put into savings. If increase_savings_weight = 0, any increase in salary will be entirely spent. 
        4. If should_clamp_absolute_spending is true, spending will be clamped to be no less than the previous year's absolute spending. (This
            matters when net income goes down. The rationale here is that reducing absolute spending is something most people would prefer to avoid.)
        5. Spending will be clamped to be no greater than after-tax income.

        0. Actually, in order to have the aforementioned mathematically-useful character of 'maxing out' or 'zeroing out' total career spending,
            the requested increase_savings_weight will actually be tweaked if the initial spending is at 95% or 5% of initial after-tax income,
            to ensure that spending is indeed maximized or minimized.
    
    """
    
    actual_increase_savings_weight = increase_savings_weight

    def increasing_savings_increasing_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        nonlocal actual_increase_savings_weight
        if previous_deltas.year == initial_year:
            # This is the first year, adjust increase_savings_weight if need be. If spending is in the upper edge region, savings weight 
            # should be decreased to push spending still higher. If it's in the lower edge region, it should be increased to push it still lower.
            # 
            initial_spending_fraction = previous_deltas.spending / previous_deltas.total_net_income
            initial_spending_fraction = min(initial_spending_fraction, 1) # Clamp to avoid weirdness
            EDGE_REGION = 0.05
            actual_increase_savings_weight = get_maxed_or_zeroed_out(1 - initial_spending_fraction, increase_savings_weight, EDGE_REGION)
            
        previous_savings_absolute = previous_deltas.total_net_income - previous_deltas.spending
        previous_savings_proportional = previous_savings_absolute / previous_deltas.total_net_income
        new_savings_proportional = previous_savings_proportional
        new_savings_for_ceiling = new_savings_proportional * deltas.total_net_income
        sp_ceiling = deltas.total_net_income - new_savings_for_ceiling # Spending ceiling: maintain proportional savings

        sp_floor = previous_deltas.spending # Spending floor: maintain absolute spending

        sp = sp_ceiling * (1 - actual_increase_savings_weight) + sp_floor * actual_increase_savings_weight

        sp_clamped = sp

        if should_clamp_absolute_spending:
            sp_clamped = max(sp, previous_deltas.spending)

        sp_clamped = min(sp_clamped, deltas.total_net_income)

        return deltas.update_spending(sp_clamped)

    return increasing_savings_increasing_spending

def get_maxed_or_zeroed_out(x : float, c_m : float, end_region_width: float):
    """
    Gets c(x), where it's assumed 0 < x < 1, and c(x) is a piecewise function such that:
     c(x) = c_m for end_region_width < x < (1 - end_region_width),
            and goes linearly to c(0) = 0 and c(1) = 1 at the ends
    """

    if x <= end_region_width:
        return x * (c_m / end_region_width)
    elif x < (1 - end_region_width):
        return c_m
    else:
        x_ = x - 1
        c_ = x_ * ((1 - c_m) / end_region_width)
        return c_ + 1
