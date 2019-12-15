import sim

class Simulation_Presenter:
    def __init__(self, simulation : sim.Simulation):
        self._simulation = simulation

    @property
    def year_of_retirement(self):
        return self._simulation.year_of_retirement
    
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
           
    @property
    def career_net_income_series(self):
        """Net income series pre-retirement"""
        return [d.total_net_income for d in self._simulation.all_deltas if d.year <= self._simulation.year_of_retirement]
    
    @property
    def career_rrsp_contribution_series(self):
        """RRSP contributions pre-retirement"""
        return [d.rrsp for d in self._simulation.all_deltas if d.year <= self._simulation.year_of_retirement]
    
    @property
    def career_tfsa_contribution_series(self):
        """RRSP contributions pre-retirement"""
        return [d.tfsa for d in self._simulation.all_deltas if d.year <= self._simulation.year_of_retirement]
    
    @property
    def career_total_savings_series(self):
        """Total savings, yearly, pre-retirement"""
        return [d.rrsp + d.tfsa for d in self._simulation.all_deltas if d.year < self._simulation.year_of_retirement]
        
    @property
    def career_total_savings_monthly_series(self):
        """Total savings, monthly, pre-retirement"""
        return [(d.rrsp + d.tfsa)/12.0 for d in self._simulation.all_deltas if d.year < self._simulation.year_of_retirement]
    
    # Retirement
    @property
    def retirement_years_series(self):
        """Years series post-retirement"""
        return [f.year for f in self._simulation.all_funds if f.year > self._simulation.year_of_retirement]

    @property
    def retirement_rrsp_withdrawal_series(self):
        return [-d.rrsp for d in self._simulation.all_deltas if d.year > self._simulation.year_of_retirement]

    @property
    def retirement_tfsa_withdrawal_series(self):
        return [-d.tfsa for d in self._simulation.all_deltas if d.year > self._simulation.year_of_retirement]
