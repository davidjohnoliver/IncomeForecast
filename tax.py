from enum import Enum
from typing import List
import datetime


class _TaxBracket:
    """
    An income tax bracket.
    """

    def __init__(self, min: float, max: float, taxRate: float):
        self.min = min
        self.max = max
        self.taxRate = taxRate


_qcBrackets = [
    _TaxBracket(0, 18952, 0),
    _TaxBracket(18952.01, 54345, 14),
    _TaxBracket(54345.01, 108680, 19),
    _TaxBracket(108680.01, 132245, 24),
    _TaxBracket(132245.01, 0, 25.75),
]

# The federal basic personal amount (BPA) has a base amount, reflected as the 0%
# bracket below, plus an "enhanced" amount available to low and middle earners.
# The enhanced amount is reduced linearly across the second-highest (29%) bracket
# and disappears entirely once income reaches the top (33%) bracket.
federalPersonalAmount = 14829  # Base BPA (the amount every taxpayer receives).
federalMaxPersonalAmount = 16452  # Maximum BPA, including the enhanced amount.
_caBrackets = [
    _TaxBracket(0, federalPersonalAmount, 0),
    _TaxBracket(federalPersonalAmount + 0.1, 58523, 14),
    _TaxBracket(58523.01, 117045, 20.5),
    _TaxBracket(117045.01, 181440, 26),
    _TaxBracket(181440.01, 258482, 29),
    _TaxBracket(258482.01, 0, 33),
]

_qcAbatement = 16.5  # https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-440-refundable-quebec-abatement.html


def get_income_tax_from_brackets(
    taxable_income: float, abatement: float, brackets: List[_TaxBracket]
):
    totalTax = 0
    amountTaxed = 0

    for bracket in brackets:
        if taxable_income >= bracket.min:
            amountTaxed = taxable_income - bracket.min

        if taxable_income > bracket.max and bracket.max > 0:
            amountTaxed = bracket.max - bracket.min

        rate = bracket.taxRate * (1 - abatement / 100.0)
        totalTax += amountTaxed * rate / 100.0

        if taxable_income <= bracket.max:
            break

    return totalTax


def get_enhanced_bpa_credit(taxable_income: float, abatement: float):
    """
    Returns the federal tax credit from the enhanced (income-tested) portion of
    the basic personal amount.

    The base BPA is already reflected as the 0% bracket in _caBrackets. The
    enhanced amount on top of it is reduced linearly for income between the
    bottom of the 29% bracket and the bottom of the 33% bracket, vanishing
    entirely at the top bracket. The credit is valued at the lowest federal
    marginal rate and, for Quebec residents, reduced by the Quebec abatement.
    """

    enhanced_amount = federalMaxPersonalAmount - federalPersonalAmount
    phaseout_start = _caBrackets[4].min
    phaseout_end = _caBrackets[4].max
    lowest_rate = _caBrackets[1].taxRate

    if taxable_income <= phaseout_start:
        remaining_amount = enhanced_amount
    elif taxable_income >= phaseout_end:
        remaining_amount = 0
    else:
        fraction_removed = (taxable_income - phaseout_start) / (
            phaseout_end - phaseout_start
        )
        remaining_amount = enhanced_amount * (1 - fraction_removed)

    rate = lowest_rate * (1 - abatement / 100.0)
    return remaining_amount * rate / 100.0


def get_income_tax(taxable_income: float):
    """
    Returns the total income tax owed for the nominated amount of taxable income (earned in Quebec by a Quebec resident).
    """

    assert datetime.datetime.now().year == 2026 # Marginal tax brackets should be kept up to date.

    caTax = get_income_tax_from_brackets(taxable_income, _qcAbatement, _caBrackets)
    caTax -= get_enhanced_bpa_credit(taxable_income, _qcAbatement)
    caTax = max(caTax, 0)
    qcTax = get_income_tax_from_brackets(taxable_income, 0, _qcBrackets)
    total = caTax + qcTax
    return total
