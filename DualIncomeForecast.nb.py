# %%

## Imports
import math
from IPython.core.display import display
import sim
import solve
import couple_rulesets
import present
import matplotlib.pyplot as plt
import plot_utils
import display_utils
from display_utils import set
from display_utils import with_colour
from display_utils import br

import IPython.display

##############################################################################

simulation = sim.Dual_Income_Simulation()
partner1 = simulation.partner1_parameters
partner2 = simulation.partner2_parameters

# Configuration

## Fill in details for the first person in the couple:
## Given name?
partner1.name = "Partner 1"

### When were you born?
partner1.year_of_birth = set.this.value

### When will simulated-you retire?
partner1.age_at_retirement = set.this.value
### Good news: the sooner you die, the less money you need to save!
partner1.age_at_death = set.this.value

### What's your current salary?
partner1.initial_salary = set.this.value
### What savings do you currently have?
partner1.initial_savings_rrsp = set.this.value
partner1.initial_savings_tfsa = set.this.value

### Where do you predict your salary will eventually peak at? (In the simulation, it will plateau at this value.)
partner1.salary_plateau = set.this.value
### By what rate do you predict your salary to increase per year, on average, up to its peak? (Eg, if you expect it to increase by 5% each year, put 'salary_compound_rate=0.05')
partner1.salary_compound_rate = set.this.value

## Fill in details for the second person in the couple:
## Given name?
partner2.name = "Partner 2"

### When were you born?
partner2.year_of_birth = set.this.value

### When will simulated-you retire?
partner2.age_at_retirement = set.this.value
### Good news: the sooner you die, the less money you need to save!
partner2.age_at_death = set.this.value

### What's your current salary?
partner2.initial_salary = set.this.value
### What savings do you currently have?
partner2.initial_savings_rrsp = set.this.value
partner2.initial_savings_tfsa = set.this.value

### Where do you predict your salary will eventually peak at? (In the simulation, it will plateau at this value.)
partner2.salary_plateau = set.this.value
### By what rate do you predict your salary to increase per year, on average, up to its peak? (Eg, if you expect it to increase by 5% each year, put 'salary_compound_rate=0.05')
partner2.salary_compound_rate = set.this.value

## Fill in additional details:
### In what year is the simulation starting? (Typically the current year)
simulation.initial_year = set.this.value

### How much money should be left over at the end? (What do you want your beneficiaries to inherit?)
simulation.final_savings = 0

### How much interest do your invested savings earn? This depends on your investments, which in turn depends on your risk tolerance, time horizon, etc. (If your interests have an annual return of, eg, 6%, put 'interest_rate = 0.06')
interest_rate = 0.08

### How should the simulation try to distribute your contributions to retirement saving? The higher the value of increase_savings_weight, the more of any increase in salary will be put towards increased saving; the lower the value, the more of any increase in salary will be put towards immediate increased spending instead. Either way, the simulation will find an overall spending vs. savings balance that will allow you to maintain a steady income in retirement; the effect of this parameter is to determine when the bulk of savings occur. A high increase_savings_weight will 'back-load' savings, giving a higher spending early, but with less increase in spending over time; whereas a low increase_savings_weight will 'front-load' savings, giving a lower spending earlier on, but a more significant increase over time.
increase_savings_weight = 0.5

### Should the simulation try to optimize the way your savings are made? If should_optimize is set to True, the simulation will try to find the balance of investment contributions over time, across different investment types and for both individuals, which will maximize lifetime spending. (Cha-ching!) This is good! But it also takes noticeably longer to run. (And sometimes it doesn't work.) We recommend you to set this to True when you've finalized the other parameters.
should_optimize = False

## Some final parameters to tweak, for the adventurous. If should_optimize = True, the simulation will search for optimum values for these parameters, using the provided values as initial guesses.
### The proportion of savings to be put in the TFSA. initial_tfsa is used in the first year, final_tfsa is used in the last year of working before retirement, and intermediate values scale linearly between the two.
initial_tfsa = 0.5
final_tfsa = 0.5
### The equalize_income_weighting parameter is used to determine how to distribute RRSP contributions between partners with unequal salaries. A high parameter value maximises the contribution of the higher-earning couple, to minimize marginal tax right now; a low parameter value spreads the contribution evenly, to minimize marginal tax later when withdrawing from the RRSP. Again, it scales linearly during the simulation from the initial value in the first year to the final value in the last year.
initial_equalize_income_weighting = 0.5
final_equalize_income_weighting = 0.5
### A correction factor used when determining how to take from RRSP vs TFSA during retirement.
rrsp_adjustment = 0.05


##############################################################################

# Simulation code, you shouldn't normally need to modify this.


optimize = solve.Optimizing_Solver(solve.binary_solver, should_invert=True)
optimize.is_optimization_disabled = not should_optimize
simulation.set_solver(optimize.solve)

ruleset = couple_rulesets.bad_seed(
    partner1.salary_compound_rate,
    partner1.salary_plateau,
    partner2.salary_compound_rate,
    partner2.salary_plateau,
    simulation.initial_year,
    increase_savings_weight,
    initial_tfsa,
    final_tfsa,
    initial_equalize_income_weighting,
    final_equalize_income_weighting,
    partner1.year_of_retirement,
    partner2.year_of_retirement,
    simulation.final_year,
    rrsp_adjustment,
    interest_rate,
    interest_rate,
    optimize,
)

simulation.set_ruleset(ruleset)

simulation.run()

##############################################################################

# Text output
if not simulation.was_solution_found:
    display(
        with_colour(
            "**No solution was found for given inputs! Showing closest outcome.**",
            "red",
        )
    )
    display(with_colour(f"Message: {simulation.run_message}", "red"))
else:
    display(with_colour("Solution found.", "green"))

display(br())

presenter = present.Dual_Income_Simulation_Presenter(simulation)


def dround(raw: float):
    zeroes = int(math.log10(raw)) - 1
    zeroes = min(3, zeroes)  # Don't round to more than 1000
    return f"${int(round(raw, -zeroes)):,.0f}"


def perc(raw: float):
    return f"{raw*100:.1f}%"


## Info table
info_table = display_utils.table("Simulation details", "")
info_table.set_alignments("--:", ":--")
info_table.append_row(f"{partner1.name} retires in:", partner1.year_of_retirement)
info_table.append_row(f"{partner2.name} retires in:", partner2.year_of_retirement)
info_table.append_row(
    f"{partner1.name}'s salary:",
    f"\${partner1.initial_salary:,.0f} to \${partner1.salary_plateau:,.0f}, increasing by {perc(partner1.salary_compound_rate)} each year",
)
info_table.append_row(
    f"{partner2.name}'s salary:",
    f"\${partner2.initial_salary:,.0f} to \${partner2.salary_plateau:,.0f}, increasing by {perc(partner2.salary_compound_rate)} each year",
)
info_table.append_row("Interest rate:", perc(interest_rate))
info_table.append_row("Increase savings weight", increase_savings_weight)
display(info_table.close())

display(br())

## Summary text
display(
    with_colour(
        f"{partner1.name} worked until {partner1.year_of_retirement}. {partner2.name} worked until {partner2.year_of_retirement}. In the first year ({presenter.years_series[1]}) they spent {dround(presenter.first_year_spending)}. In retirement they had an income of {dround(presenter.retirement_spending)} a year. Their lifetime average yearly spending was {dround(presenter.average_yearly_spending)} a year.",
        "black",
    )
)

display(br())


## Savings table
savings_table = display_utils.table(
    "Year",
    f"{partner1.name}'s salary",
    f"{partner2.name}'s salary",
    "Monthly spending",
    "Monthly saving",
)
YEARS_TO_SHOW_SAVINGS_FOR = 5
for i in range(1, YEARS_TO_SHOW_SAVINGS_FOR + 1):
    savings_table.append_row(
        f"**{presenter.years_series[i]}**",
        dround(presenter.partner1.salary_series[i]),
        dround(presenter.partner2.salary_series[i]),
        dround(presenter.spending_monthly_series[i]),
        dround(presenter.combined_savings_monthly_series[i]),
    )
display(savings_table.close())

display(br())

## Detailed savings table
savings_breakdown_table = display_utils.table(
    "Year",
    f"{partner1.name} TFSA",
    f"{partner1.name} RRSP",
    f"{partner2.name} TFSA",
    f"{partner2.name} RRSP",
)
for i in range(1, YEARS_TO_SHOW_SAVINGS_FOR + 1):
    savings_breakdown_table.append_row(
        f"**{presenter.years_series[i]}**",
        dround(presenter.partner1.tfsa_monthly_series[i]),
        dround(presenter.partner1.rrsp_monthly_series[i]),
        dround(presenter.partner2.tfsa_monthly_series[i]),
        dround(presenter.partner2.rrsp_monthly_series[i]),
    )
display(with_colour("Detailed savings breakdown, monthly contributions:", "black"))
display(savings_breakdown_table.close())

# %%
# General-interest graphs

base_fig_size = (10, 4)


def fig_size(stretch_y: float = 1):
    return (base_fig_size[0], base_fig_size[1] * stretch_y)


fig1, ax1 = plt.subplots(figsize=fig_size())

ax1.plot(
    presenter.partner1.career_year_series,
    presenter.partner1.career_salary_series,
    "-",
    label=f"{partner1.name}",
)
ax1.plot(
    presenter.partner2.career_year_series,
    presenter.partner2.career_salary_series,
    "-",
    label=f"{partner2.name}",
)
ax1.set_title("Salary")
ax1.legend()

fig2, ax2 = plt.subplots(figsize=fig_size())
ax2.plot(presenter.years_series, presenter.spending_monthly_series, "-")
ax2.set_title("Monthly spending")

fig3, ax3 = plt.subplots(figsize=fig_size())
ax3.plot(presenter.career_years_series, presenter.career_combined_savings_monthly_series)
ax3.set_title("Monthly total saving")

# fig4, ax4 = plt.subplots(figsize=fig_size())
# ax4.plot(presenter.partner1.career_year_series,presenter.partner1.career_tfsa_monthly_series, '-', label=f"{partner1.name} TFSA")
# ax4.plot(presenter.partner1.career_year_series,presenter.partner1.career_rrsp_monthly_series, '-', label=f"{partner1.name} RRSP")
# ax4.plot(presenter.partner2.career_year_series,presenter.partner2.career_tfsa_monthly_series, '-', label=f"{partner2.name} TFSA")
# ax4.plot(presenter.partner2.career_year_series,presenter.partner2.career_rrsp_monthly_series, '-', label=f"{partner2.name} RRSP")
# ax4.set_title("Monthly saving breakdown")
# ax4.legend()

plt.show()

# %%
# Re-import modified dependencies
import importlib
import present
import sim
import couple_rulesets
import couple_spending_rules
import couple_savings_rules
import solve
import display_utils

importlib.reload(present)
importlib.reload(sim)
importlib.reload(couple_rulesets)
importlib.reload(couple_spending_rules)
importlib.reload(solve)
importlib.reload(display_utils)
importlib.reload(couple_savings_rules)

display("Reimported modules")

# %%
# %%
