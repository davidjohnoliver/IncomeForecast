import utils


class funds_state:
    """Stores total RRSP savings and total TFSA savings for a given year."""

    def __init__(self, rrsp_savings, tfsa_savings, year):
        self.rrsp_savings = rrsp_savings
        self.tfsa_savings = tfsa_savings
        self.year = year


class deltas_state:
    """Records deltas for a given year, including pre-tax salary, income tax, RRSP contribution, TFSA contribution, and spending."""

    def __init__(self, year, gross_salary, tax, rrsp, tfsa, spending, rrsp_interest, tfsa_interest, tax_refund):
        self._year = year
        self._gross_salary = gross_salary
        self._tax = tax
        self._rrsp = rrsp
        self._tfsa = tfsa
        self._spending = spending
        self._rrsp_interest = rrsp_interest
        self._tfsa_interest = tfsa_interest
        self._tax_refund = tax_refund

    @classmethod
    def from_year(cls, year):
        return deltas_state(year, 0, 0, 0, 0, 0, 0, 0, 0)

    def _copy(self):
        output = deltas_state(self.year, self.gross_salary, self.tax, self.rrsp,
                              self.tfsa, self.spending, self.rrsp_interest, self.tfsa_interest, self._tax_refund)
        return output

    @property
    def year(self):
        """The year property."""
        return self._year

    def update_year(self, new_value):
        output = self._copy()
        output._year = new_value
        return output

    @property
    def gross_salary(self):
        """Pre-tax salary."""
        return self._gross_salary

    def update_gross_salary(self, new_value):
        output = self._copy()
        output._gross_salary = new_value
        return output

    @property
    def tax(self):
        """Income tax."""
        return self._tax

    def update_tax(self, new_value):
        output = self._copy()
        output._tax = new_value
        return output

    @property
    def rrsp(self):
        """RRSP contribution."""
        return self._rrsp

    def update_rrsp(self, new_value):
        output = self._copy()
        output._rrsp = new_value
        return output

    @property
    def tfsa(self):
        """TFSA contribution"""
        return self._tfsa

    def update_tfsa(self, new_value):
        output = self._copy()
        output._tfsa = new_value
        return output

    @property
    def spending(self):
        """Total spending."""
        return self._spending

    def update_spending(self, new_value):
        output = self._copy()
        output._spending = new_value
        return output

    @property
    def rrsp_interest(self):
        """Interest earned from RRSP."""
        return self._rrsp_interest

    def update_rrsp_interest(self, new_value):
        output = self._copy()
        output._rrsp_interest = new_value
        return output

    @property
    def tfsa_interest(self):
        """Interest earned from TFSA."""
        return self._tfsa_interest

    def update_tfsa_interest(self, new_value):
        output = self._copy()
        output._tfsa_interest = new_value
        return output

    @property
    def tax_refund(self):
        """Tax refund received."""
        return self._tax_refund

    def update_tax_refund(self, new_value):
        output = self._copy()
        output._tax_refund = new_value
        return output

    @property
    def total_income(self):
        """Salary plus tax refund."""
        return self.gross_salary + self.tax_refund

    @property
    def taxable_income(self):
        """Taxable portion of salary, ie less the RRSP contribution."""
        return self.gross_salary - self.rrsp


def get_updated_funds_from_deltas(previous_funds: funds_state, deltas: deltas_state):
    """Applies a set of deltas to a funds state, and returns the corresponding updated funds state.

       RRSP contributions and interest are added to the RRSP, TFSA contributions and interest are added to the TFSA."""
    assert deltas.year == previous_funds.year + 1
    # TODO: tax refund
    return funds_state(previous_funds.rrsp_savings + deltas.rrsp + deltas._rrsp_interest, previous_funds.tfsa_savings + deltas.tfsa + deltas._tfsa_interest, deltas.year)


def get_updated_deltas_from_rules(previous_funds: funds_state, previous_deltas: deltas_state, rules):
    """Applies the provided list of rules in sequence to produce a set of deltas. The signature for a rule is:
     def rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state)
    Each rule operates on the output of the previous rule."""
    assert previous_funds.year == previous_deltas.year
    deltas = deltas_state.from_year(previous_funds.year + 1)
    for rule in rules:
        deltas = rule(deltas, previous_funds, previous_deltas)

    return deltas
