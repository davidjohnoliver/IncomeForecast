import sim
import model

def test_simulation_run():
    simulation = sim.Simulation()
    simulation.retirement_age = 60 # So, 2050
    simulation.year_of_birth = 1990
    simulation.initial_year = 2020
    simulation.age_at_death = 70 # Smoker?
    simulation.savings_at_death = -1 #Ignored - we're not testing Simulation
    simulation._initial_savings_rrsp = 4000
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

    run = sim.Simulation_Run(simulation, initial_spending)

    run.run()
    # A ver: initial (rrsp) = 4k; 30 x (53k - 42k) = 30 x 11k = 330k; 10 x 29k = 290k; final savings = 44k
    assert 334000 == run.funds_at_retirement.total_savings
    assert 169000 == run.funds_at_retirement.rrsp_savings
    assert 165000 == run.funds_at_retirement.tfsa_savings

    assert 44000 == run.final_funds.total_savings
    assert 24000 == run.final_funds.rrsp_savings
    assert 20000 == run.final_funds.tfsa_savings