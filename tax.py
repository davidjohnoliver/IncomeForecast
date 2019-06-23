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
    _TaxBracket(0, 15269, 0),
    _TaxBracket(15269.01, 43790, 15),
    _TaxBracket(43790.01, 87575, 20),
    _TaxBracket(87575.01, 106555, 24),
    _TaxBracket(106555.01, 0, 25.75),
]

_caBrackets = [
    _TaxBracket(0, 12069, 0),
    _TaxBracket(12069.01, 47630, 15),
    _TaxBracket(47630.01, 95259, 20.5),
    _TaxBracket(95259.01, 147667, 26),
    _TaxBracket(147667.01, 210371, 29),
    _TaxBracket(210371.01, 0, 33),
]

_qcAbatement = 16.5  # https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-440-refundable-quebec-abatement.html


def get_income_tax_from_brackets(taxable_income: float, abatement: float, brackets: List[_TaxBracket]):
    totalTax = 0
    amountTaxed = 0

    for bracket in brackets:
        if (taxable_income >= bracket.min):
            amountTaxed = taxable_income - bracket.min

        if (taxable_income > bracket.max and bracket.max > 0):
            amountTaxed = bracket.max - bracket.min

        rate = bracket.taxRate * (1 - abatement/100.)
        totalTax += amountTaxed * rate/100.

        if (taxable_income <= bracket.max):
            break

    return totalTax


def get_income_tax(taxable_income: float):
    """
    Returns the total income tax owed for the nominated amount of taxable income (earned in Quebec by a Quebec resident).
    """

    assert datetime.datetime.now().year == 2019 # Marginal tax brackets should be kept up to date.

    caTax = get_income_tax_from_brackets(
        taxable_income, _qcAbatement, _caBrackets)
    qcTax = get_income_tax_from_brackets(taxable_income, 0, _qcBrackets)
    total = caTax + qcTax
    return total
