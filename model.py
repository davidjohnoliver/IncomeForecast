"""
Base state classes and update logic. 
"""

class funds_state:
    """Stores total RRSP savings and total TFSA savings for a given year."""

    @property
    def total_savings(self):
        """Total savings across all classes."""
        return self.rrsp_savings + self.tfsa_savings

    def __init__(self, rrsp_savings, tfsa_savings, year):
        self.rrsp_savings = rrsp_savings
        self.tfsa_savings = tfsa_savings
        self.year = year


class couple_funds_state:
    """Stores funds states for two income-earners in a couple."""

    def __init__(self, partner1_funds : funds_state, partner2_funds : funds_state):
        assert(partner1_funds.year == partner2_funds.year)
        self.partner1_funds = partner1_funds
        self.partner2_funds = partner2_funds

    @classmethod
    def from_savings(partner1_rrsp_savings : float, partner1_tfsa_savings: float, partner2_rrsp_savings : float, partner2_tfsa_savings: float, year : int) -> None:
        partner1_funds = funds_state(partner1_rrsp_savings, partner1_tfsa_savings, year)
        partner2_funds = funds_state(partner2_rrsp_savings, partner2_tfsa_savings, year)
        return couple_funds_state(partner1_funds, partner2_funds)

    @property
    def year(self):
        assert(self.partner1_funds.year == self.partner2_funds.year)
        return self.partner1_funds.year

class deltas_state:
    """Records deltas for a given year, including pre-tax salary, income tax, RRSP contribution, TFSA contribution, and spending. Immutable, 
    call update_x() to create a mutated value with modified x."""

    def __init__(self, year: int, gross_salary, tax, rrsp, tfsa, spending, rrsp_interest, tfsa_interest, tax_refund):
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
    def from_year(cls, year: int):
        return deltas_state(year, 0, 0, 0, 0, 0, 0, 0, 0)

    def _copy(self):
        output = deltas_state(self.year, self.gross_salary, self.tax, self.rrsp,
                              self.tfsa, self.spending, self.rrsp_interest, self.tfsa_interest, self._tax_refund)
        return output

#region Immutable properties
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
#endregion

    @property
    def total_net_income(self):
        """Salary plus tax refund (from last year) minus tax owed."""
        return self.gross_salary + self.tax_refund - self.tax

    @property
    def taxable_income(self):
        """Taxable portion of salary, ie less the RRSP contribution (or mas the withdrawal), plus any interest earned on RRSP savings (TFSA interest isn't taxed)."""
        return self.gross_salary - self.rrsp + self.rrsp_interest

    @property
    def undifferentiated_savings(self):
        """Total savings available to be split between RRSP and TFSA. """
        return self.total_net_income - self.spending


class couple_deltas_state:
    """Records deltas for a given year for two income-earners in a couple."""

    def __init__(self, partner1_deltas : deltas_state, partner2_deltas : deltas_state) -> None:
        assert(partner1_deltas.year == partner2_deltas.year)
        self._partner1_deltas = partner1_deltas
        self._partner2_deltas = partner2_deltas

    def from_year(year: int):
        return couple_deltas_state(deltas_state.from_year(year), deltas_state.from_year(year))

    def copy(self):
        output = couple_deltas_state(self._partner1_deltas, self._partner2_deltas)
        return output

    @property
    def partner1_deltas(self):
        return self._partner1_deltas

    def update_partner1_deltas(self, new_value : deltas_state):
        output = self.copy()
        output._partner1_deltas = new_value
        return output

    @property
    def partner2_deltas(self):
        return self._partner2_deltas

    def update_partner2_deltas(self, new_value : deltas_state):
        output = self.copy()
        output._partner2_deltas = new_value
        return output

    @property
    def year(self):
        assert(self.partner1_deltas.year == self.partner2_deltas.year)
        return self.partner1_deltas.year



def get_updated_funds_from_deltas(previous_funds: funds_state, deltas: deltas_state):
    """Applies a set of deltas to a funds state, and returns the corresponding updated funds state.

       RRSP contributions and interest are added to the RRSP, TFSA contributions and interest are added to the TFSA."""
    assert deltas.year == previous_funds.year + 1
    return funds_state(previous_funds.rrsp_savings + deltas.rrsp + deltas.rrsp_interest, previous_funds.tfsa_savings + deltas.tfsa + deltas.tfsa_interest, deltas.year)


def get_updated_deltas_from_rules(previous_funds: funds_state, previous_deltas: deltas_state, rules):
    """Applies the provided list of rules in sequence to produce a set of deltas. The signature for a rule is:
     def rule(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state)
    Each rule operates on the output of the previous rule.
    
    The output deltas are for the year subsequent to that of previous_funds and previous_deltas."""
    
    assert previous_funds.year == previous_deltas.year
    deltas = deltas_state.from_year(previous_funds.year + 1)
    for rule in rules:
        deltas = rule(deltas, previous_funds, previous_deltas)

    return deltas


def get_updated_couple_funds_from_deltas(previous_funds: couple_funds_state, deltas: couple_deltas_state):
    """Applies a set of deltas to a couple funds state, and returns the corresponding updated funds state."""
    return couple_funds_state(
        get_updated_funds_from_deltas(previous_funds.partner1_funds, deltas._partner1_deltas),
        get_updated_funds_from_deltas(previous_funds.partner2_funds, deltas._partner2_deltas)
    )

def get_updated_couple_deltas_from_rules(previous_funds: couple_funds_state, previous_deltas: couple_deltas_state, rules):
    """
    Applies the provided list of couple rules in sequence to produce a set of deltas.

    The signature for a couples rule is:
    def rule(deltas: model.couple_deltas_state, previous_funds: model.couple_funds_state, previous_deltas: model.couple_deltas_state)
    """

    assert previous_funds.year == previous_deltas.year
    deltas = couple_deltas_state.from_year(previous_funds.year + 1)
    for rule in rules:
        deltas = rule(deltas, previous_funds, previous_deltas)
    
    return deltas

def get_couple_rule_from_single_rule(single_rule, partner: int):
    """Wraps a rule for an individual income-earner as a rule for a dual-income couple, applied to one person in the couple."""
    if (partner < 1 or partner > 2):
        raise ValueError
    
    def apply_partner1(deltas: couple_deltas_state, previous_funds: couple_funds_state, previous_deltas: couple_deltas_state):
        new_partner1_deltas = single_rule(deltas.partner1_deltas, previous_funds.partner1_funds, previous_deltas.partner1_deltas)
        new_deltas = deltas.update_partner1_deltas(new_partner1_deltas)
        return new_deltas
    
    def apply_partner2(deltas: couple_deltas_state, previous_funds: couple_funds_state, previous_deltas: couple_deltas_state):
        new_partner2_deltas = single_rule(deltas.partner2_deltas, previous_funds.partner2_funds, previous_deltas.partner2_deltas)
        new_deltas = deltas.update_partner2_deltas(new_partner2_deltas)
        return new_deltas

    return apply_partner1 if partner == 1 else apply_partner2
        
    

