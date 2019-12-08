import sim
import model
import solve
import math

def test_simulation_run():
    simulation = sim.Simulation()
    simulation.age_at_retirement = 60 # So, 2050
    simulation.year_of_birth = 1990
    simulation.initial_year = 2020
    simulation.age_at_death = 70 # Smoker?
    simulation.savings_at_death = -1 #Ignored - we're not testing Simulation
    simulation.initial_savings_rrsp = 4000
    simulation.initial_savings_tfsa = 0
    simulation.initial_salary = 53000

    retirement_income = 29000
    initial_spending = 42000

    #rules
    def constant_salary(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(previous_deltas.gross_salary)

    def constant_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(previous_deltas.spending)

    def split50_50(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        output = deltas.update_rrsp(deltas.undifferentiated_savings * 0.5)
        output = output.update_tfsa(deltas.undifferentiated_savings * 0.5)
        return output

    def retirement_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(retirement_income)

    simulation.set_rules([ constant_salary, constant_spending, split50_50 ])
    simulation.set_retirement_rules([ retirement_spending, split50_50 ])

    simulation_run = sim.Simulation_Run(simulation, initial_spending)

    simulation_run.run()
    # A ver: initial (rrsp) = 4k; 30 x (53k - 42k) = 30 x 11k = 330k; 10 x 29k = 290k; final savings = 44k
    assert 334000 == simulation_run.funds_at_retirement.total_savings
    assert 169000 == simulation_run.funds_at_retirement.rrsp_savings
    assert 165000 == simulation_run.funds_at_retirement.tfsa_savings

    assert 44000 == simulation_run.final_funds.total_savings
    assert 24000 == simulation_run.final_funds.rrsp_savings
    assert 20000 == simulation_run.final_funds.tfsa_savings

def test_simulation():
    simulation = sim.Simulation()
    simulation.age_at_retirement = 60 # So, 2050
    simulation.year_of_birth = 1990
    simulation.initial_year = 2020
    simulation.age_at_death = 70 # Smoker?
    simulation.savings_at_death = 44000 # Reverse-engineered from previous test
    simulation.initial_savings_rrsp = 4000
    simulation.initial_savings_tfsa = 0
    simulation.initial_salary = 53000

    retirement_income = 29000
    expected_initial_spending = 42000

    #rules
    def constant_salary(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(previous_deltas.gross_salary)

    def constant_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(previous_deltas.spending)

    def split50_50(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        output = deltas.update_rrsp(deltas.undifferentiated_savings * 0.5)
        output = output.update_tfsa(deltas.undifferentiated_savings * 0.5)
        return output

    def retirement_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(retirement_income)

    simulation.set_rules([ constant_salary, constant_spending, split50_50 ])
    simulation.set_retirement_rules([ retirement_spending, split50_50 ])

    assert -1 == simulation.required_initial_spending

    simulation.set_solver(solve.binary_solver)

    simulation.run()

    assert math.isclose(expected_initial_spending, simulation.required_initial_spending, rel_tol=0.01)

def test_simulation_optimizing_solver_unoptimized():
    simulation = sim.Simulation()
    simulation.age_at_retirement = 60 # So, 2050
    simulation.year_of_birth = 1990
    simulation.initial_year = 2020
    simulation.age_at_death = 70 # Smoker?
    simulation.savings_at_death = 44000 # Reverse-engineered from previous test
    simulation.initial_savings_rrsp = 4000
    simulation.initial_savings_tfsa = 0
    simulation.initial_salary = 53000

    retirement_income = 29000
    expected_initial_spending = 42000

    #rules
    def constant_salary(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(previous_deltas.gross_salary)

    def constant_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(previous_deltas.spending)

    def split50_50(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        output = deltas.update_rrsp(deltas.undifferentiated_savings * 0.5)
        output = output.update_tfsa(deltas.undifferentiated_savings * 0.5)
        return output

    def retirement_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(retirement_income)

    simulation.set_rules([ constant_salary, constant_spending, split50_50 ])
    simulation.set_retirement_rules([ retirement_spending, split50_50 ])

    assert -1 == simulation.required_initial_spending

    opt = solve.Optimizing_Solver(solve.binary_solver, should_invert = True)

    simulation.set_solver(opt.solve)

    simulation.run()

    assert math.isclose(expected_initial_spending, simulation.required_initial_spending, rel_tol=0.01)

def test_simulation_optimizing_solver():
    simulation = sim.Simulation()
    simulation.age_at_retirement = 60 # So, 2050
    simulation.year_of_birth = 1990
    simulation.initial_year = 2020
    simulation.age_at_death = 70 # Smoker?
    simulation.savings_at_death = 44000 # Reverse-engineered from previous test
    simulation.initial_savings_rrsp = 4000
    simulation.initial_savings_tfsa = 0
    simulation.initial_salary = 53000

    retirement_income = 29000
    expected_initial_spending = 42000

    opt = solve.Optimizing_Solver(solve.binary_solver, should_invert = True)

    #rules
    def constant_salary(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_gross_salary(previous_deltas.gross_salary)

    def constant_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(previous_deltas.spending)

    def split50_50(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        output = deltas.update_rrsp(deltas.undifferentiated_savings * 0.5)
        output = output.update_tfsa(deltas.undifferentiated_savings * 0.5)
        return output

    def retirement_spending(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        return deltas.update_spending(retirement_income)

    dr_func = opt.subscribe_optimized_scalar("Drain", -1000, 5000)

    def throw_money_down_drain(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        dr = dr_func()
        return deltas.update_gross_salary(deltas.gross_salary - abs(dr - 318))

    simulation.set_rules([ constant_salary, throw_money_down_drain, constant_spending, split50_50 ])
    simulation.set_retirement_rules([ retirement_spending, split50_50 ])

    assert -1 == simulation.required_initial_spending


    simulation.set_solver(opt.solve)

    simulation.run()

    assert math.isclose(expected_initial_spending, simulation.required_initial_spending, rel_tol=0.01)
    assert math.isclose(318, opt.get_optimized_value("Drain"), rel_tol=0.01)