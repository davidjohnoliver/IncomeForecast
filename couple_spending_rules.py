import model
import spending_rules


def get_luxury_over_basic(base_spending: float, luxury_compound_rate: float):
    """
    Models expenditure as a compounding 'luxury' component added to a fixed 'basic needs' component.

    sp[y] = b + (1 + c)sp[y-1], where sp = spending, b = base_spending, c = luxury_compound_rate
    """

    def luxury_over_basic(
        deltas: model.couple_deltas_state,
        previous_funds: model.couple_funds_state,
        previous_deltas: model.couple_deltas_state,
    ):
        if (
            deltas.partner1_deltas.gross_salary == 0
            and deltas.partner2_deltas.gross_salary == 0
        ):
            # If no one's earning money, assume they're retired, and maintain constant spending
            return deltas.update_household_spending(previous_deltas.household_spending)
        previous_luxury = previous_deltas.household_spending - base_spending
        if previous_luxury < 0:
            # Try to somehow handle spending below the 'basic level,' since the solver will try spendings from 0 upwards. Consumer code
            # is responsible for warning the user if the actual solution returns a spending below the 'basic' level.
            new_spending = (
                1 + luxury_compound_rate
            ) * previous_deltas.household_spending
            return deltas.update_household_spending(new_spending)

        new_luxury = (1 + luxury_compound_rate) * previous_luxury
        return deltas.update_household_spending(base_spending + new_luxury)

    return luxury_over_basic


def get_increasing_savings_increasing_spending(
    initial_year: float, increase_savings_weight: float
):
    """
    A somewhat complex spending rule which tries to enforce the following intuitively desirable traits:
        - savings, as a fraction of after-tax income, never decreases;
        - spending, in absolute dollars, never decreases.

    Where it's not possible to have both, the latter takes priority. Ie, if net income falls (or goes to zero, as will happen when both
    partners retire), then savings may need to decrease or indeed go negative, but spending can never decrease. (Outer layers of the simulation are
    responsible for reconciling this with modeled salary progressions and final targets.)

    It also has the following mathematically useful characteristics:
        - if the initial savings is 0 (ie initial spending == initial after-tax income), then total career savings will be very close to 0
        - if the initial spending is 0, then total career spending will be very close to 0
    (These characteristics maximise the ability to find a solution for a given income function and savings target)

    The increase_savings_weight normalized parameter determines the priority of increasing saving vs increasing spending, assuming both are possible.
    If not, as mentioned, maintaining spending takes priority.) At its maximum value, lifetime salary increases will be entirely saved; at its minimum
    value, lifetime salary increases will be entirely spent. From the perspective of a simulation being run to find a spending curve consistent with a
    particular final savings level (eg breaking even, leaving an inheritance of $100k, etc), what this means is that a high increase_savings_weight will
    'back-load' savings, giving a higher spending early, but with less increase in spending over time; whereas a low increase_savings_weight will 'front-load'
     savings, giving a lower spending earlier on, but a more significant increase over time.

    It determines the spending per-year as follows:
        1. The spending that would maintain the same proportional savings is taken as a ceiling, call this sp_ceil
        2. The spending that would maintain the same absolute spending (ie the previous year's value) is taken as sp_floor
        3. Actual spending is sp = sp_ceil*(1 - increase_savings_weight) + sp_floor*increase_savings_weight.
            Hence if increase_savings_weight = 0.5, the average will be taken. If increase_savings_weight = 1, any increase in salary will be
            entirely put into savings. If increase_savings_weight = 0, any increase in salary will be entirely spent.
        4. Spending will be clamped to be no less than the previous year's absolute spending. (This matters when net income goes down. The rationale
            here is that reducing absolute spending is something most people would prefer to avoid. Additionally, after retirement, spending should stay
            at the level it reached prior to retirement.)

        0. Actually, in order to have the aforementioned mathematically-useful character of 'maxing out' or 'zeroing out' total career spending,
            the requested increase_savings_weight will be tweaked if the initial spending is at 95% or 5% of initial after-tax income,
            to ensure that spending is indeed maximized or minimized.
    """

    actual_increase_savings_weight = increase_savings_weight

    def increasing_savings_increasing_spending(
        deltas: model.couple_deltas_state,
        previous_funds: model.couple_funds_state,
        previous_deltas: model.couple_deltas_state,
    ):
        nonlocal actual_increase_savings_weight
        if previous_deltas.year == initial_year:
            # This is the first year, adjust increase_savings_weight if need be. If spending is in the upper edge region, savings weight
            # should be decreased to push spending still higher. If it's in the lower edge region, it should be increased to push it still lower.
            #
            # The rationale is for total savings to approach 0 as initial savings approaches 0, and total spending to approach 0 as initial spending
            # approaches 0. This trait of the function maximises the chance of finding a consistent solution for a given target.
            initial_spending_fraction = (
                previous_deltas.household_spending
                / previous_deltas.household_total_net_income
            )
            initial_spending_fraction = min(
                initial_spending_fraction, 1
            )  # Clamp to avoid weirdness
            EDGE_REGION = 0.05
            actual_increase_savings_weight = spending_rules.get_maxed_or_zeroed_out(
                1 - initial_spending_fraction, increase_savings_weight, EDGE_REGION
            )

        previous_savings_absolute = (
            previous_deltas.household_total_net_income
            - previous_deltas.household_spending
        )
        previous_savings_proportional = (
            previous_savings_absolute / previous_deltas.household_total_net_income
        )
        new_savings_proportional = previous_savings_proportional
        new_savings_for_ceiling = (
            new_savings_proportional * deltas.household_total_net_income
        )
        sp_ceiling = (
            deltas.household_total_net_income - new_savings_for_ceiling
        )  # Spending ceiling: maintain proportional savings

        sp_floor = (
            previous_deltas.household_spending
        )  # Spending floor: maintain absolute spending

        sp = (
            sp_ceiling * (1 - actual_increase_savings_weight)
            + sp_floor * actual_increase_savings_weight
        )  # Interpolate actual spending according to weighting

        sp_clamped = max(
            sp, previous_deltas.household_spending
        )  # Make sure spending never decreases

        return deltas.update_household_spending(sp_clamped)

    return increasing_savings_increasing_spending
