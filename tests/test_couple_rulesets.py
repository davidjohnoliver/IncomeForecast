import sim
import couple_rulesets
import solve


def test_alice_runs():

    simulation = sim.Dual_Income_Simulation()

    simulation.partner1_parameters.age_at_retirement = 60
    simulation.partner1_parameters.year_of_birth = 1990
    simulation.partner1_parameters.age_at_death = 80
    simulation.partner1_parameters.initial_salary = 40000
    simulation.partner1_parameters.initial_savings_rrsp = 5000
    simulation.partner1_parameters.initial_savings_tfsa = 600

    simulation.partner2_parameters.age_at_retirement = 64
    simulation.partner2_parameters.year_of_birth = 1989
    simulation.partner2_parameters.age_at_death = 75
    simulation.partner2_parameters.initial_salary = 60000
    simulation.partner2_parameters.initial_savings_rrsp = 2000
    simulation.partner2_parameters.initial_savings_tfsa = 800

    simulation.initial_year = 2025
    simulation.final_savings = 10000

    simulation.set_solver(solve.binary_solver)

    simulation.set_ruleset(
        couple_rulesets.alice(0.06, 80000, 0.04, 75000, 60000, 0.05, 0.1, 0.1)
    )

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)
