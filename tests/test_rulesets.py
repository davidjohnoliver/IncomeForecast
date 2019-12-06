import rulesets
import sim
import solve

def test_ampere_runs():
    """
    This is a minimal sanity-test that using the ruleset doesn't throw any errors. It doesn't verify correctness (which isn't really possible for full rulesets).
    """

    simulation = sim.Simulation()
    simulation.age_at_retirement = 60
    simulation.year_of_birth = 1990
    simulation.initial_year = 2025
    simulation.age_at_death = 80
    simulation.savings_at_death = 10000
    simulation.initial_salary = 40000
    simulation._initial_savings_rrsp = 5000
    simulation.initial_savings_tfsa = 600

    simulation.set_solver(solve.binary_solver)

    career_rules, retirement_rules = rulesets.ampere(
        salary_compound_rate=0.05,
        salary_plateau=70000,
        base_spending=30000,
        spending_luxury_compound_rate=0.04,
        initial_rrsp_allotment=0.5,
        final_rrsp_allotment=0.5,
        initial_year=simulation.initial_year,
        year_of_retirement=simulation.year_of_retirement,
        year_of_death=simulation.year_of_death,
        retirement_income=50000,
        rrsp_interest_rate=0.05,
        tfsa_interest_rate=0.05
    )

    simulation.set_rules(career_rules)
    simulation.set_retirement_rules(retirement_rules)

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)

def test_bose_runs():
    """
    This is a minimal sanity-test that using the ruleset doesn't throw any errors. It doesn't verify correctness (which isn't really possible for full rulesets).
    """

    simulation = sim.Simulation()
    simulation.age_at_retirement = 60
    simulation.year_of_birth = 1990
    simulation.initial_year = 2025
    simulation.age_at_death = 80
    simulation.savings_at_death = 10000
    simulation.initial_salary = 40000
    simulation._initial_savings_rrsp = 5000
    simulation.initial_savings_tfsa = 600

    simulation.set_solver(solve.binary_solver)

    career_rules, retirement_rules = rulesets.bose(
        salary_compound_rate=0.05,
        salary_plateau=70000,
        base_spending=30000,
        spending_luxury_compound_rate=0.04,
        cap_fractional=0.9,
        initial_rrsp_allotment=0.5,
        final_rrsp_allotment=0.5,
        initial_year=simulation.initial_year,
        year_of_retirement=simulation.year_of_retirement,
        year_of_death=simulation.year_of_death,
        retirement_income=50000,
        rrsp_interest_rate=0.05,
        tfsa_interest_rate=0.05
    )

    simulation.set_rules(career_rules)
    simulation.set_retirement_rules(retirement_rules)

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)

def test_curie_runs():
    """
    This is a minimal sanity-test that using the ruleset doesn't throw any errors. It doesn't verify correctness (which isn't really possible for full rulesets).
    """

    simulation = sim.Simulation()
    simulation.age_at_retirement = 60
    simulation.year_of_birth = 1990
    simulation.initial_year = 2025
    simulation.age_at_death = 80
    simulation.savings_at_death = 10000
    simulation.initial_salary = 40000
    simulation._initial_savings_rrsp = 5000
    simulation.initial_savings_tfsa = 600

    optimize = solve.Optimizing_Solver(solve.binary_solver, should_invert=True)

    simulation.set_solver(optimize.solve)

    career_rules, retirement_rules = rulesets.curie(
        salary_compound_rate=0.05,
        salary_plateau=70000,
        base_spending=30000,
        spending_luxury_compound_rate=0.04,
        cap_fractional=0.9,
        initial_year=simulation.initial_year,
        year_of_retirement=simulation.year_of_retirement,
        year_of_death=simulation.year_of_death,
        retirement_income=50000,
        rrsp_interest_rate=0.05,
        tfsa_interest_rate=0.05,
        optimize=optimize
    )

    simulation.set_rules(career_rules)
    simulation.set_retirement_rules(retirement_rules)

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)

def test_dirac_runs():
    """
    This is a minimal sanity-test that using the ruleset doesn't throw any errors. It doesn't verify correctness (which isn't really possible for full rulesets).
    """

    simulation = sim.Simulation()
    simulation.age_at_retirement = 60
    simulation.year_of_birth = 1990
    simulation.initial_year = 2025
    simulation.age_at_death = 80
    simulation.savings_at_death = 10000
    simulation.initial_salary = 40000
    simulation._initial_savings_rrsp = 5000
    simulation.initial_savings_tfsa = 600

    optimize = solve.Optimizing_Solver(solve.binary_solver, should_invert=True)

    simulation.set_solver(optimize.solve)

    career_rules, retirement_rules = rulesets.dirac(
        salary_compound_rate=0.05,
        salary_plateau=70000,
        base_spending=30000,
        spending_luxury_compound_rate=0.04,
        cap_fractional=0.9,
        initial_year=simulation.initial_year,
        year_of_retirement=simulation.year_of_retirement,
        year_of_death=simulation.year_of_death,
        retirement_income=50000,
        rrsp_interest_rate=0.05,
        tfsa_interest_rate=0.05,
        optimize=optimize
    )

    simulation.set_rules(career_rules)
    simulation.set_retirement_rules(retirement_rules)

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)

def test_einstein_runs():
    """
    This is a minimal sanity-test that using the ruleset doesn't throw any errors. It doesn't verify correctness (which isn't really possible for full rulesets).
    """

    simulation = sim.Simulation()
    simulation.age_at_retirement = 60
    simulation.year_of_birth = 1990
    simulation.initial_year = 2025
    simulation.age_at_death = 80
    simulation.savings_at_death = 10000
    simulation.initial_salary = 40000
    simulation._initial_savings_rrsp = 5000
    simulation.initial_savings_tfsa = 600

    simulation.set_solver(solve.binary_solver)

    career_rules, retirement_rules = rulesets.einstein(
        salary_compound_rate=0.05,
        salary_plateau=70000,
        base_spending=30000,
        increase_savings_weight=0.5,
        initial_rrsp_allotment=0.5,
        final_rrsp_allotment=0.5,
        initial_year=simulation.initial_year,
        year_of_retirement=simulation.year_of_retirement,
        year_of_death=simulation.year_of_death,
        retirement_income=50000,
        rrsp_interest_rate=0.05,
        tfsa_interest_rate=0.05
    )

    simulation.set_rules(career_rules)
    simulation.set_retirement_rules(retirement_rules)

    simulation.run()

    assert 46 == len(simulation.all_deltas)
    assert 46 == len(simulation.all_funds)