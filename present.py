import sim
import model
import statistics
from typing import List


class Simulation_Presenter:
    def __init__(self, simulation: sim.Simulation):
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
        return [
            f.year
            for f in self._simulation.all_funds
            if f.year <= self._simulation.year_of_retirement
        ]

    @property
    def career_salary_series(self):
        """Salary series pre-retirement"""
        return [
            d.gross_salary
            for d in self._simulation.all_deltas
            if d.year <= self._simulation.year_of_retirement
        ]

    @property
    def career_net_income_series(self):
        """Net income series pre-retirement"""
        return [
            d.total_net_income
            for d in self._simulation.all_deltas
            if d.year <= self._simulation.year_of_retirement
        ]

    @property
    def career_rrsp_contribution_series(self):
        """RRSP contributions pre-retirement"""
        return [
            d.rrsp
            for d in self._simulation.all_deltas
            if d.year <= self._simulation.year_of_retirement
        ]

    @property
    def career_tfsa_contribution_series(self):
        """RRSP contributions pre-retirement"""
        return [
            d.tfsa
            for d in self._simulation.all_deltas
            if d.year <= self._simulation.year_of_retirement
        ]

    @property
    def career_total_savings_series(self):
        """Total savings, yearly, pre-retirement"""
        return [
            d.rrsp + d.tfsa
            for d in self._simulation.all_deltas
            if d.year < self._simulation.year_of_retirement
        ]

    @property
    def career_total_savings_monthly_series(self):
        """Total savings, monthly, pre-retirement"""
        return [
            (d.rrsp + d.tfsa) / 12.0
            for d in self._simulation.all_deltas
            if d.year < self._simulation.year_of_retirement
        ]

    # Retirement
    @property
    def retirement_years_series(self):
        """Years series post-retirement"""
        return [
            f.year
            for f in self._simulation.all_funds
            if f.year > self._simulation.year_of_retirement
        ]

    @property
    def retirement_rrsp_withdrawal_series(self):
        return [
            -d.rrsp
            for d in self._simulation.all_deltas
            if d.year > self._simulation.year_of_retirement
        ]

    @property
    def retirement_tfsa_withdrawal_series(self):
        return [
            -d.tfsa
            for d in self._simulation.all_deltas
            if d.year > self._simulation.year_of_retirement
        ]


class Individual_Presenter:
    def __init__(
        self,
        partner_params: sim.Individual_Parameters,
        all_deltas: List[model.deltas_state],
    ) -> None:
        self._partner_params = partner_params
        self._all_deltas = all_deltas

    @property
    def salary_series(self):
        """Salary series"""
        return [d.gross_salary for d in self._all_deltas]

    @property
    def tfsa_series(self):
        return [d.tfsa for d in self._all_deltas]

    @property
    def tfsa_monthly_series(self):
        return [t / 12 for t in self.tfsa_series]

    @property
    def rrsp_series(self):
        return [d.rrsp for d in self._all_deltas]

    @property
    def rrsp_monthly_series(self):
        return [t / 12 for t in self.rrsp_series]

    @property
    def career_salary_series(self):
        return [d.gross_salary for d in self._all_deltas if d.gross_salary > 0]

    @property
    def career_year_series(self):
        return [d.year for d in self._all_deltas if d.gross_salary > 0]

    @property
    def career_tfsa_series(self):
        return [d.tfsa for d in self._all_deltas if d.gross_salary > 0]

    @property
    def career_tfsa_monthly_series(self):
        return [t/12 for t in self.career_tfsa_series]

    @property
    def career_rrsp_series(self):
        return [d.rrsp for d in self._all_deltas if d.gross_salary > 0]

    @property
    def career_rrsp_monthly_series(self):
        return [t/12 for t in self.career_rrsp_series]


class Dual_Income_Simulation_Presenter:
    def __init__(self, simulation: sim.Dual_Income_Simulation):
        self._simulation = simulation
        self._partner1 = Individual_Presenter(
            self._partner1_deltas, [cd.partner1_deltas for cd in simulation.all_deltas]
        )
        self._partner2 = Individual_Presenter(
            self._partner2_deltas, [cd.partner2_deltas for cd in simulation.all_deltas]
        )

    @property
    def partner1(self):
        return self._partner1

    @property
    def partner2(self):
        return self._partner2

    @property
    def year_of_retirement(self):
        return self._simulation.year_of_retirement

    @property
    def years_series(self):
        """Years series"""
        return [f.year for f in self._simulation.all_funds]

    @property
    def career_years_series(self):
        """Years series"""
        return [
            d.year for d in self._simulation.all_deltas if self._is_someone_working(d)
        ]

    @property
    def spending_series(self):
        """Spending series"""
        return [d.household_spending for d in self._simulation.all_deltas]

    @property
    def spending_monthly_series(self):
        return [s / 12 for s in self.spending_series]

    @property
    def combined_savings_series(self):
        """p"""
        return [self._combined_savings(d) for d in self._simulation.all_deltas]

    @property
    def combined_savings_monthly_series(self):
        """p"""
        return [s / 12 for s in self.combined_savings_series]

    @property
    def career_combined_savings_series(self):
        """p"""
        return [
            self._combined_savings(d)
            for d in self._simulation.all_deltas
            if self._is_someone_working(d)
        ]

    @property
    def career_combined_savings_monthly_series(self):
        """p"""
        return [s / 12 for s in self.career_combined_savings_series]

    @property
    def retirement_spending(self):
        return self.spending_series[-1]

    @property
    def first_year_spending(self):
        return self.spending_series[1]

    @property
    def average_yearly_spending(self):
        return statistics.mean(self.spending_series)

    @property
    def _partner1_deltas(self):
        return [d.partner1_deltas for d in self._simulation.all_deltas]

    @property
    def _partner2_deltas(self):
        return [d.partner2_deltas for d in self._simulation.all_deltas]

    def _is_someone_working(self, deltas_state: model.couple_deltas_state):
        return (
            deltas_state.partner1_deltas.gross_salary > 0
            or deltas_state.partner2_deltas.gross_salary > 0
        )

    def _combined_savings(self, deltas_state: model.couple_deltas_state):
        return (
            deltas_state.partner1_deltas.tfsa
            + deltas_state.partner1_deltas.rrsp
            + deltas_state.partner2_deltas.tfsa
            + deltas_state.partner2_deltas.rrsp
        )

