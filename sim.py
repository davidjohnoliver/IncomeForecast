import model
import typing
import natural_rules

class Simulation:
    """
    A full simulation, which produces a required savings rate to achieve target given model and inputs.
    """

    @property
    def age_at_retirement(self):
        """The age at which you will retire. (Inclusive, ie this is the first year you will no longer be working.)"""
        return self._age_at_retirement
    @age_at_retirement.setter
    def age_at_retirement(self, value):
        self._age_at_retirement = value

    @property
    def year_of_birth(self):
        """The year you got born, used to calculate year of retirement."""
        return self._year_of_birth
    @year_of_birth.setter
    def year_of_birth(self, value):
        self._year_of_birth = value

    @property
    def initial_year(self):
        """The year in which the simulation begins, inclusive."""
        return self._initial_year
    @initial_year.setter
    def initial_year(self, value):
        self._initial_year = value

    @property
    def age_at_death(self):
        """How old you will be when you die. Morbid, but necessary."""
        return self._age_at_death
    @age_at_death.setter
    def age_at_death(self, value):
        self._age_at_death = value

    @property
    def savings_at_death(self):
        """The amount of savings you wish to have left over when you die."""
        return self._savings_at_death
    @savings_at_death.setter
    def savings_at_death(self, value):
        self._savings_at_death = value

    @property
    def initial_salary(self):
        """Your yearly salary at the beginning of the simulation (typically, your present salary). """
        return self._initial_salary
    @initial_salary.setter
    def initial_salary(self, value):
        self._initial_salary = value

    @property
    def initial_savings_rrsp(self):
        """The amount you already have saved in a RRSP account (or accounts) at the beginning of the simulation."""
        return self._initial_savings_rrsp
    @initial_savings_rrsp.setter
    def initial_savings_rrsp(self, value):
        self._initial_savings_rrsp = value

    @property
    def initial_savings_tfsa(self):
        """The amount you already have saved in a TFSA account (or accounts) at the beginning of the simulation."""
        return self._initial_savings_tfsa
    @initial_savings_tfsa.setter
    def initial_savings_tfsa(self, value):
        self._initial_savings_tfsa = value

    @property
    def year_of_retirement(self):
        return self.year_of_birth + self.age_at_retirement

    @property
    def year_of_death(self):
        return self.year_of_birth + self.age_at_death
    
    @property
    def required_initial_spending(self):
        """
        The initial spending required to achieve the desired final savings.
        
        Before the simulation has been run, this will be -1.
        """
        if (self._solution_run is None):
            return -1
        
        return self._solution_run._initial_spending

    @property
    def all_funds(self):
        """A list of all funds_states for the solution run, in order of year."""
        return self._solution_run.all_funds

    @property
    def all_deltas(self):
        """A list of all deltas_states for the solution run, in order of year."""
        return self._solution_run.all_deltas

    @property
    def was_solution_found(self):
        """True if running the simulation found a solution for given inputs, false if no valid solution was found, None if simulation was not run yet."""
        return self._was_solution_found

    @property
    def run_message(self):
        """Message corresponding to the outcome of the run."""
        return self._run_message
    
    def __init__(self):
        self._solution_run = None
        self._was_solution_found = None
        self._run_message = "Not run"

    def set_rules(self, rules):
        """
        Set the list of rules that will be applied sequentially each year to update model state, up until retirement. These effectively define
        the logic and assumptions of the simulation. The signature for a rule is:
        def rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state)
        """
        self._rules = rules

    def set_retirement_rules(self, rules):
        """
        Set the list of rules that will be applied sequentially each year after retirement. The signature for a rule is:
        def rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state)
        """
        self._retirement_rules = rules

    def set_solver(self, solver):
        """
        Sets the solver that will be used to find the required initial savings, and the corresponding simulation run. The signature of a solver is:
        def solver(intermediate_fn, model_fn, target_output : float, initial_lower_bound : float, initial_upper_bound : float, tolerance : float):
        """
        self._solver = solver

    def run(self):
        """
        Runs the simulation and calculates the required savings rate.
        """
        
        def create_run(initial_spending : float):
            return Simulation_Run(self, initial_spending)
        
        def run_model(simulation_run : Simulation_Run):
            simulation_run.run()
            return simulation_run.final_funds.total_savings
        
        tolerance = 0.001
        _, solution_run, was_solution_found, msg = self._solver(create_run, run_model, self.savings_at_death, 0, self.initial_salary, tolerance)
        self._set_solution_run(solution_run, was_solution_found)
        self._run_message = msg
    
    def _set_solution_run(self, solution_run : 'Simulation_Run', was_solution_found : bool):
        self._solution_run = solution_run
        self._was_solution_found = was_solution_found


class Simulation_Run:
    """
    A single run of the simulation, at a given savings rate.
    """

    def __init__(self, parent: Simulation, initial_spending):
        self._parent = parent
        self._initial_spending = initial_spending

        self._all_funds = list()
        self._all_deltas = list()

    @property
    def final_funds(self):
        """The funds at completion of the run."""
        return self._final_funds

    @property
    def funds_at_retirement(self):
        """The funds for the year of retirement."""
        return self._funds_at_retirement

    @property
    def all_funds(self) -> typing.List[model.funds_state]:
        """A list of all funds_states for the run, in order of year."""
        return self._all_funds

    @property
    def all_deltas(self) -> typing.List[model.deltas_state]:
        """A list of all deltas_states for the run, in order of year."""
        return self._all_deltas

    def run(self):
        """
        Run the simulation and set final funds.
        """
        initial_year = self._parent.initial_year
        year_of_retirement = self._parent.year_of_retirement
        year_of_death = self._parent.year_of_death

        initial_funds_state = model.funds_state(self._parent.initial_savings_rrsp, self._parent._initial_savings_tfsa, initial_year)
        initial_deltas_state = model.deltas_state(
            year=initial_year, 
            gross_salary=self._parent.initial_salary, 
            tax=0, 
            rrsp=0,
            tfsa=0,
            spending=self._initial_spending, 
            rrsp_interest=0,
            tfsa_interest=0,
            tax_refund=0
        )

        initial_deltas_state = natural_rules.apply_tax(initial_deltas_state, None, None)

        previous_deltas = initial_deltas_state
        previous_funds = initial_funds_state
        self.all_deltas.append(previous_deltas)
        self.all_funds.append(previous_funds)
        for _ in range(initial_year, year_of_retirement): # Work up until retirement
            deltas = model.get_updated_deltas_from_rules(previous_funds, previous_deltas, self._parent._rules)
            funds = model.get_updated_funds_from_deltas(previous_funds, deltas)
            self.all_deltas.append(deltas)
            self.all_funds.append(funds)
            previous_deltas = deltas
            previous_funds = funds

        self._funds_at_retirement = funds

        assert year_of_retirement == self._funds_at_retirement.year
        
        for _ in range(year_of_retirement, year_of_death): # Live off of savings up until death
            deltas = model.get_updated_deltas_from_rules(previous_funds, previous_deltas, self._parent._retirement_rules)
            funds = model.get_updated_funds_from_deltas(previous_funds, deltas)
            self.all_deltas.append(deltas)
            self.all_funds.append(funds)
            previous_deltas = deltas
            previous_funds = funds
        
        # Subsequent developments are outside scope of model
        
        self._final_funds = funds