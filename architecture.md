# Architecture of IncomeForecast

The main layers:

 - The simulation layer
 - The model layer
 - The rules layer
 - The visualization and analysis layer

## Simulation layer

### `Simulation`

The `Simulation` class is responsible for obtaining answers to questions like, 'how much do I need to save,' and 'how should I optimally distribute my savings between different investment options'. 

In addition to the various boundary conditions of the simulation, it takes a ruleset and a solver function as inputs. 

Within `Simulation` most parameters are fixed as 'facts' about the simulation (eg year in which it starts, initial salary, initial savings etc), but a few parameters will be varied across multiple runs: the initial spending level, which dictates the subsequent evolution of spending, and is the parameter being solved for; and any parameters that are being optimized by an optimizing solver, such as the split between different investment types.

### `Simulation_Run`

The `Simulation_Run` class is responsible for actually running the model. From the perspective of `Simulation_Run`, all parameters of the model are fixed.

## Model layer

The model layer defines the basic logic of IncomeForecast's model. It runs a discrete simulation where each 'tick' is one year. On each tick, the state of the model, consisting of various pots of money or `funds`, is updated according to a set of 'rules'.

### `model.get_updated_deltas_from_rules`

The `deltas_state` is the set of changes, or deltas, that will be applied to the state. A rule is simply a function that takes the current `deltas_state`, as well as other information (the `funds` after the previous year, the previous `deltas_state`) and returns a new `deltas_state`. Different rules may calculate the new `deltas_state` in a number of ways, described below.

The `get_updated_deltas_from_rules` applies a list of rules in order, chaining them so that the output `deltas_state` of the previous rule is supplied to the next. This allows rules to have an implicit logical dependence on other rules.

### `model.get_updated_funds_from_deltas`

Applies `deltas_state` to a `funds_state`, incrementing each fund type according to the relevant delta values.

## Solving and optimizing

A 'solver' in the program is a function with a defined signature which tries to find the numeric input that produces a given target numeric output, for a pair of model functions and a range of allowed inputs. The first model function takes the numeric input and outputs an intermediate object, which is anticipated to be of later interest (in current usage in the program, this will be a `Simulation_Run`, but the solver doesn't care). The second model function takes the intermediate object as input and produces a numeric output.

The solver returns a 4-ple with the solution input, the intermediate object corresponding to the solution, a boolean indicating whether a solution was actually found, and a status message. 

It may be that no valid solution for the given parameters could be found, in which case the first two values of the tuple will normally come from whatever step the solver ended on. (It's convenient for subsequent analysis and user troubleshooting to have these values even if they don't represent a valid solution.)

### `binary_solver`

This implementation assumes that the model function is monotonic and simply does a binary search within the allowed input range, calling the model function repeatedly, until a solution is found to the desired tolerance or the range is exhausted. 

### `Optimizing_Solver`

The `Optimizing_Solver` wraps a solver implementation to additionally provide optimization. Whereas a simple solver like `binary_solver` finds the unique numeric input that produces the target output for a set of fixed simulation parameters, `Optimizing_Solver` finds the _minimized_ (or maximized) input that produces the target output, by optimizing one or more variable parameters. It reports both the minimum input found as well as the optimal parameter values.

`Optimizing_Solver` exposes the `subscribe_optimized_scalar()` method, which registers an optimizable parameter by name, with (optionally) a lower and upper bound as well as a specific initial guess, and returns a getter function that will return the value of the parameter for the current optimization run. The getter function is typically consumed by one of the rules within the model.

Internally it uses the [Nelder-Mead method](https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method), which is numerically robust to the 'staircase-like output' often produced by IncomeForecast.

## Rules and rulesets

The rules supplied to the model define the detailed content and behaviour of the simulation. Recall that a rule is a function that calculates fund deltas based on the current state of the simulation and the output of earlier rules in the same tick. Although all rules have the same external signature and can in principle modify any and all deltas they wish, in practice rules fall into one of several conceptual categories.

### Natural rules

The term 'natural' is used for "rules that are set by law, economics and/or mathematics, as opposed to rules that articulate the assumptions of the forecasting model." In other words, these rules articulate 'simple facts about the world'. These include rules to apply tax and tax refunds; and calculating investment interest, for a given interest rate.

### Salary rule

A salary rule describes how gross (pre-tax) salary evolves over the course of the simulation. Typically there's one salary rule in use for a given model run. 

It's usually a reasonable assumption that the output of the salary rule is independent of the output of other rules: people earn however much they're earning at any given time.

The challenge faced by the salary rule is to give a conservative but realistic predicted estimate of an unknown future. In many fields, depending on the stage of their career, people can expect that their salary will increase in the future, but without knowing exactly when or by how much. The salary rule is the most uncertain and speculative part of the model.

### Spending (vs. saving) rule

A spending rule determines the division of after-tax income between spending and saving.

The job of the spending rule is to find a balance between spending right now, and saving to spend after retirement. There's no 'uncertainty' in the spending rule as such, since it represents a recommendation rather than a prediction. Instead, the challenge with the spending rule is an entirely technical, but not at all trivial, one of supplying a heuristic that is mathematically tractable (since the spending rule is the main target of the solver in the outer layer of the program) and intuitively appealing.

### Savings allocation rule

After total savings has been determined, a savings allocation rule divides the funds allocated to be saved between different specific savings options. At the moment these are the two 'registered' investment options in Canada (Tax-free Savings Accounts and Registered Retirement Savings Plans); the model doesn't currently account for taxable regular investments, or contribution limits to tax-free/tax-deferred registered investments.

The savings allocation rule is, like the spending vs. saving rule, a recommendation not a prediction, and one that the user is presumably fairly indifferent to, beyond the goal of minimising the amount they need to save to achieve a given retirement goal.

### Career and retirement phases

There are two phases to the model, the career period (where the user is in the workforce and earning money) and the retirement period (the user is retired and living off their savings). Both these phases are modelled in the same way, by applying rules to update the available funds; the only difference is in the rules applied. 

The retirement-phase rules are inherently simpler, since there's no longer a salary to model, nor savings contributions to make decisions about; the main decision in this phase is which pool (ie which type of investment) to deduct from to meet living expenses. (Again, the user is presumably indifferent on this question beyond the goal of optimizing their lifestyle expenditures.)

### Rulesets

A ruleset is a sequence of rules that completely describe a simulation. Typically a ruleset consists of a salary progression rule, a spending vs. saving rule, a savings allocation rule, and as many natural rules as are needed. 

## Visualization and post-processing

Visualization and post-simulation analysis (such as there is) takes place in the same Jupyter Notebook used to configure and run the simulation.

 - Table showing prescribed savings (per month and per year) for the first 5 years of the simulation, ie the key actionable information, as well as income figures for additional context
 - Time plot of per-year salary and spending
 - Time plot showing cumulative savings, split by investment type, up until and subsequent to retirement
 - Time plot showing per-year savings contributions (withdrawals) for different investment types