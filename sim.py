import model
import typing
import natural_rules

class Simulation:
    """
    A full simulation, which produces a required savings rate to achieve target given model and inputs for a single income earner.
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

class Individual_Parameters:
    """Simulation parameters for a single individual in a dual-income simulation."""

    @property
    def age_at_retirement(self):
        """The age at which this person will retire. (Inclusive, ie this is the first year they will no longer be working.)"""
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
    def age_at_death(self):
        """How old you will be when you die. Morbid, but necessary."""
        return self._age_at_death
    @age_at_death.setter
    def age_at_death(self, value):
        self._age_at_death = value

    @property
    def initial_salary(self):
        """This person's yearly salary at the beginning of the simulation (typically, their present salary). """
        return self._initial_salary
    @initial_salary.setter
    def initial_salary(self, value):
        self._initial_salary = value

    @property
    def initial_savings_rrsp(self):
        """The amount this person already has saved in a RRSP account (or accounts) at the beginning of the simulation."""
        return self._initial_savings_rrsp
    @initial_savings_rrsp.setter
    def initial_savings_rrsp(self, value):
        self._initial_savings_rrsp = value

    @property
    def initial_savings_tfsa(self):
        """The amount this person already has saved in a TFSA account (or accounts) at the beginning of the simulation."""
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

    def is_retired(self, year : int):
        return year >= self.year_of_retirement

class Dual_Income_Simulation:
    """A simulation which produces the required savings rates for a dual-income couple."""

    @property
    def initial_year(self):
        """The calendar year in which the simulation begins, inclusive."""
        return self._initial_year
    @initial_year.setter
    def initial_year(self, value : int):
        self._initial_year = value

    @property
    def partner1_parameters(self):
        """Simulation parameters for the first person."""
        return self._partner1_parameters
    @partner1_parameters.setter
    def partner1_parameters(self, value : Individual_Parameters):
        self._partner1_parameters = value

    @property
    def partner2_parameters(self):
        """Simulation parameters for the second person."""
        return self._partner2_parameters
    @partner2_parameters.setter
    def partner2_parameters(self, value : Individual_Parameters):
        self._partner2_parameters = value

    @property
    def final_year(self):
        """The final year of the simulation, defined, I'm afraid, as the year that the last partner dies."""
        return max(self.partner1_parameters.year_of_death, self.partner2_parameters.year_of_death)

    @property
    def initial_combined_salary(self):
        """The sum of each partner's initial salaries."""
        return self.partner1_parameters.initial_salary + self.partner2_parameters.initial_salary

    @property
    def final_savings(self):
        """The savings desired to have remaining when both partners have ceased to consume resources."""
        return self._final_savings
    @final_savings.setter
    def final_savings(self, value : float):
        self._final_savings = value
    
    @property
    def required_initial_spending(self):
        """
        The initial spending required to achieve the desired final savings.
        
        This represents the outcome of the simulation. Before the simulation has been run, this will be -1.
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

        self._partner1_parameters = Individual_Parameters()
        self._partner2_parameters = Individual_Parameters()

    def set_ruleset(self, ruleset):
        """
        Sets the ruleset which provides couple rules that set the behaviour of the simulation. The signature of a ruleset is:
        def ruleset(current_year : int, is_partner1_retired : bool, is_partner2_retired : bool) -> List[rule], where the signature of a rule is:
        def rule(deltas: model.couple_deltas_state, previous_funds: model.couple_funds_state, previous_deltas: model.couple_deltas_state)

        Note there's no separate 'retirement rules' as for a single-income simulation, because the ruleset has to support a scenario where 
        one person is still working and the other has retired.
        """
        self._ruleset = ruleset
    

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
            return Dual_Income_Simulation_Run(self, initial_spending)
        
        def run_model(simulation_run : Dual_Income_Simulation_Run):
            simulation_run.run()
            return simulation_run.final_funds.total_savings
        
        tolerance = 0.001
        _, solution_run, was_solution_found, msg = self._solver(create_run, run_model, self.final_savings, 0, self.initial_combined_salary, tolerance)
        self._set_solution_run(solution_run, was_solution_found)
        self._run_message = msg
    
    def _set_solution_run(self, solution_run : 'Dual_Income_Simulation_Run', was_solution_found : bool):
        self._solution_run = solution_run
        self._was_solution_found = was_solution_found



class Dual_Income_Simulation_Run:
    """
    A single run of a dual-income simulation, at a given savings rate.
    """

    def __init__(self, parent: Dual_Income_Simulation, initial_spending : float):
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
    def all_funds(self) -> typing.List[model.couple_funds_state]:
        """A list of all funds_states for the run, in order of year."""
        return self._all_funds

    @property
    def all_deltas(self) -> typing.List[model.couple_deltas_state]:
        """A list of all deltas_states for the run, in order of year."""
        return self._all_deltas

    def _get_initial_deltas_state_from_params(self, partner_params : Individual_Parameters):
        initial_deltas_state = model.deltas_state(
            year=self._parent.initial_year, 
            gross_salary=partner_params.initial_salary, 
            tax=0, 
            rrsp=0,
            tfsa=0,
            spending=0, # spending is tracked at the household level
            rrsp_interest=0,
            tfsa_interest=0,
            tax_refund=0
        )

        initial_deltas_state = natural_rules.apply_tax(initial_deltas_state, None, None)

        return initial_deltas_state

    def _get_initial_funds_state_from_params(self, partner_params : Individual_Parameters):
        return model.funds_state(partner_params.initial_savings_rrsp, partner_params.initial_savings_tfsa, self._parent.initial_year)

    def run(self):
        partner1_params = self._parent.partner1_parameters
        partner2_params = self._parent.partner2_parameters
        initial_funds_state = model.couple_funds_state(
            self._get_initial_funds_state_from_params(partner1_params),
            self._get_initial_funds_state_from_params(partner2_params)
        )

        initial_deltas_state = model.couple_deltas_state(
            self._get_initial_deltas_state_from_params(partner1_params),
            self._get_initial_deltas_state_from_params(partner2_params),
            self._initial_spending
        )

        previous_deltas = initial_deltas_state
        previous_funds = initial_funds_state
        self.all_deltas.append(previous_deltas)
        self.all_funds.append(previous_funds)
        
        for year in range(self._parent.initial_year, self._parent.final_year):
            rules = self._parent._ruleset(year, partner1_params.is_retired(year), partner2_params.is_retired(year))
            deltas = model.get_updated_couple_deltas_from_rules(previous_funds, previous_deltas, rules)
            funds = model.get_updated_couple_funds_from_deltas(previous_funds, deltas)
            self.all_deltas.append(deltas)
            self.all_funds.append(funds)
            previous_deltas = deltas
            previous_funds = funds
        
        self._final_funds = funds
