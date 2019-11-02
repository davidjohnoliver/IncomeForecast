import sim

class Simulation_Presenter:
    def __init__(self, simulation : sim.Simulation):
        self._simulation = simulation
    
    @property
    def years_series(self):
        """Years series"""
        return [f.year for f in self._simulation.all_funds]
    
    @property
    def spending_series(self):
        """Spending series"""
        return [d.spending for d in self._simulation.all_deltas]
   
    @property
    def salary_series(self):
        """Salary series"""
        return [d.gross_salary for d in self._simulation.all_deltas]
    
    @property
    def rrsp_total_series(self):
        """Accumulated RRSP series"""
        return [f.rrsp_savings for f in self._simulation.all_funds]
    
    @property
    def tfsa_total_series(self):
        """Accumulated TFSA series"""
        return [f.tfsa_savings for f in self._simulation.all_funds]

    @property
    def savings_total_series(self):
        """Accumulated total savings series"""
        return [f.total_savings for f in self._simulation.all_funds]
    
    # Career
    @property
    def career_years_series(self):
        """Years series pre-retirement"""
        return [f.year for f in self._simulation.all_funds if f.year <= self._simulation.year_of_retirement]
           
    @property
    def career_salary_series(self):
        """Salary series pre-retirement"""
        return [d.gross_salary for d in self._simulation.all_deltas if d.year <= self._simulation.year_of_retirement]
    
    # Retirement
    @property
    def retirement_years_series(self):
        """Years series post-retirement"""
        return [f.year for f in self._simulation.all_funds if f.year > self._simulation.year_of_retirement]