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
    _TaxBracket(0, 15728, 0),
    _TaxBracket(15728.01, 45105, 15),
    _TaxBracket(45105.01, 90200, 20),
    _TaxBracket(90200.01, 109755, 24),
    _TaxBracket(109755.01, 0, 25.75),
]

federalPersonalAmount = 13808
_caBrackets = [
    _TaxBracket(0, federalPersonalAmount, 0),
    _TaxBracket(federalPersonalAmount+0.1, 49020, 15),
    _TaxBracket(49020.01, 98040, 20.5),
    _TaxBracket(98040.01, 151978, 26),
    _TaxBracket(151978.01, 216511, 29.32),
    _TaxBracket(216511.01, 0, 33),
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

    assert datetime.datetime.now().year == 2021 # Marginal tax brackets should be kept up to date.

    caTax = get_income_tax_from_brackets(
        taxable_income, _qcAbatement, _caBrackets)
    qcTax = get_income_tax_from_brackets(taxable_income, 0, _qcBrackets)
    total = caTax + qcTax
    return total
