# Guidance for contributing to IncomeForecast

## Summary
This repo models retirement savings (for Quebec, Canada) using a small, well-layered Python simulation.

## Style and coding conventions
The code uses type-safety as much as is possible with Python.

Function calls with 3 or more parameters should use named arguments for all parameters. Eg:
```
    previous_funds = model.funds_state(
        rrsp_savings=0.0,
        tfsa_savings=0.0,
        year=2000,
        unregistered_savings=0.0,
        tfsa_limit=1000.0,
        rrsp_limit=0.0,
    )
```

## Adding code
 - When adding new code to an existing file, the new code should 'look like' the existing code in the same file. (Eg if existing function parameters don't have default values, new parameters shouldn't either.) Stick to existing patterns and conventions.
 - Modify test code to accommodate production code, not the other way around.

## Overall architecture
- Layers:
  - Simulation layer: `sim.Simulation` and `sim.Simulation_Run` orchestrate runs and use a pluggable `solver` to find the initial spending that meets a target (`sim.Simulation.run`).
  - Model layer: `model.funds_state`, `model.deltas_state`, `model.get_updated_deltas_from_rules`, `model.get_updated_funds_from_deltas` handle per-year state updates.
  - Rules layer: small functions (see `salary_rules.py`, `spending_rules.py`, `savings_rules.py`, `natural_rules.py`, `couple_*_rules.py`) compose a run. `ruleset.get_career_rules` and `ruleset.get_retirement_rules` assemble ordered rule lists.
  - Solver & Optimizer

Primary entrypoint for humans is `IncomeForecast.ipynb`. Core code is in `sim.py`, `model.py`, `ruleset.py`, `rules_*` modules, `solve.py`, and `natural_rules.py`.

### Details
- Rule signature: every rule has the same signature: `rule(deltas, previous_funds, previous_deltas)` and MUST return an updated deltas object (not mutate in-place). See `model.get_updated_deltas_from_rules` and tests in `tests/` for examples.
  - Example (from tests):
    def constant_salary(deltas, previous_funds, previous_deltas):
        return deltas.update_gross_salary(previous_deltas.gross_salary)
- Use the immutable-style `deltas_state.update_x()` helpers (they copy and return a new deltas object). Do not modify `deltas` or `previous_deltas` in-place.

## Fences
 - don't make changes to test_get_income_tax unless explicitly instructed to.
