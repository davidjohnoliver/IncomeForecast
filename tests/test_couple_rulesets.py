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
    simulation.partner1_parameters.initial_savings_unregistered = 0
    simulation.partner1_parameters.initial_tfsa_limit = 0
    simulation.partner1_parameters.initial_rrsp_limit = 0

    simulation.partner2_parameters.age_at_retirement = 64
    simulation.partner2_parameters.year_of_birth = 1989
    simulation.partner2_parameters.age_at_death = 75
    simulation.partner2_parameters.initial_salary = 60000
    simulation.partner2_parameters.initial_savings_rrsp = 2000
    simulation.partner2_parameters.initial_savings_tfsa = 800
    simulation.partner2_parameters.initial_savings_unregistered = 0
    simulation.partner2_parameters.initial_tfsa_limit = 0
    simulation.partner2_parameters.initial_rrsp_limit = 0

    simulation.initial_year = 2025
    simulation.final_savings = 10000

    simulation.set_solver(solve.binary_solver)

    simulation.set_ruleset(
        couple_rulesets.alice(0.06, 80000, 0.04, 75000, 60000, 0.05, 0.1, 0.1)
    )

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)


def test_bad_seed_runs():

    simulation = sim.Dual_Income_Simulation()

    simulation.partner1_parameters.age_at_retirement = 60
    simulation.partner1_parameters.year_of_birth = 1990
    simulation.partner1_parameters.age_at_death = 80
    simulation.partner1_parameters.initial_salary = 40000
    simulation.partner1_parameters.initial_savings_rrsp = 5000
    simulation.partner1_parameters.initial_savings_tfsa = 600
    simulation.partner1_parameters.initial_savings_unregistered = 0
    simulation.partner1_parameters.initial_tfsa_limit = 0
    simulation.partner1_parameters.initial_rrsp_limit = 0

    simulation.partner2_parameters.age_at_retirement = 64
    simulation.partner2_parameters.year_of_birth = 1989
    simulation.partner2_parameters.age_at_death = 75
    simulation.partner2_parameters.initial_salary = 60000
    simulation.partner2_parameters.initial_savings_rrsp = 2000
    simulation.partner2_parameters.initial_savings_tfsa = 800
    simulation.partner2_parameters.initial_savings_unregistered = 0
    simulation.partner2_parameters.initial_tfsa_limit = 0
    simulation.partner2_parameters.initial_rrsp_limit = 0

    simulation.initial_year = 2025
    simulation.final_savings = 10000

    optimize = solve.Optimizing_Solver(solve.binary_solver, should_invert=True)

    simulation.set_solver(optimize.solve)

    simulation.set_ruleset(
        couple_rulesets.bad_seed(
            0.06,
            80000,
            0.04,
            75000,
            simulation.initial_year,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            simulation.partner1_parameters.year_of_retirement,
            simulation.partner2_parameters.year_of_retirement,
            simulation.final_year,
            0,
            0.05,
            0.05,
            optimize,
        )
    )

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)


def test_charlie_runs():

    simulation = sim.Dual_Income_Simulation()

    simulation.partner1_parameters.age_at_retirement = 60
    simulation.partner1_parameters.year_of_birth = 1990
    simulation.partner1_parameters.age_at_death = 80
    simulation.partner1_parameters.initial_salary = 40000
    simulation.partner1_parameters.initial_savings_rrsp = 5000
    simulation.partner1_parameters.initial_savings_tfsa = 600
    simulation.partner1_parameters.initial_savings_unregistered = 0
    simulation.partner1_parameters.initial_tfsa_limit = 10000
    simulation.partner1_parameters.initial_rrsp_limit = 20000

    simulation.partner2_parameters.age_at_retirement = 64
    simulation.partner2_parameters.year_of_birth = 1989
    simulation.partner2_parameters.age_at_death = 75
    simulation.partner2_parameters.initial_salary = 60000
    simulation.partner2_parameters.initial_savings_rrsp = 2000
    simulation.partner2_parameters.initial_savings_tfsa = 800
    simulation.partner2_parameters.initial_savings_unregistered = 0
    simulation.partner2_parameters.initial_tfsa_limit = 10000
    simulation.partner2_parameters.initial_rrsp_limit = 20000

    simulation.initial_year = 2025
    simulation.final_savings = 10000

    optimize = solve.Optimizing_Solver(solve.binary_solver, should_invert=True)

    simulation.set_solver(optimize.solve)

    simulation.set_ruleset(
        couple_rulesets.charlie(
            0.06,
            80000,
            0.04,
            75000,
            simulation.initial_year,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            simulation.partner1_parameters.year_of_retirement,
            simulation.partner2_parameters.year_of_retirement,
            simulation.final_year,
            0,
            0.05,
            0.05,
            0.02,
            6000,
            0.18,
            30000,
            optimize,
            0,
            0,
            0
        )
    )

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)


def test_charlie_with_mortgage_runs():

    simulation = sim.Dual_Income_Simulation()

    simulation.partner1_parameters.age_at_retirement = 60
    simulation.partner1_parameters.year_of_birth = 1990
    simulation.partner1_parameters.age_at_death = 80
    simulation.partner1_parameters.initial_salary = 40000
    simulation.partner1_parameters.initial_savings_rrsp = 5000
    simulation.partner1_parameters.initial_savings_tfsa = 600
    simulation.partner1_parameters.initial_savings_unregistered = 0
    simulation.partner1_parameters.initial_tfsa_limit = 10000
    simulation.partner1_parameters.initial_rrsp_limit = 20000

    simulation.partner2_parameters.age_at_retirement = 64
    simulation.partner2_parameters.year_of_birth = 1989
    simulation.partner2_parameters.age_at_death = 75
    simulation.partner2_parameters.initial_salary = 60000
    simulation.partner2_parameters.initial_savings_rrsp = 2000
    simulation.partner2_parameters.initial_savings_tfsa = 800
    simulation.partner2_parameters.initial_savings_unregistered = 0
    simulation.partner2_parameters.initial_tfsa_limit = 10000
    simulation.partner2_parameters.initial_rrsp_limit = 20000

    simulation.initial_year = 2025
    simulation.final_savings = 10000

    optimize = solve.Optimizing_Solver(solve.binary_solver, should_invert=True)

    simulation.set_solver(optimize.solve)

    simulation.set_ruleset(
        couple_rulesets.charlie(
            0.06,
            80000,
            0.04,
            75000,
            simulation.initial_year,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            simulation.partner1_parameters.year_of_retirement,
            simulation.partner2_parameters.year_of_retirement,
            simulation.final_year,
            0,
            0.05,
            0.05,
            0.02,
            6000,
            0.18,
            30000,
            optimize,
            mortgage_principal=300000,
            mortgage_amortization=25,
            mortgage_interest=0.04,
        )
    )

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)

    # Verify mortgage payment is present in the first year where rules are applied
    assert simulation.all_deltas[1].household_debt_payments > 0
