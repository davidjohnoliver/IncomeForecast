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

federalPersonalAmount = 14829
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


def get_income_tax(taxable_income: float):
    """
    Returns the total income tax owed for the nominated amount of taxable income (earned in Quebec by a Quebec resident).
    """

    assert datetime.datetime.now().year == 2026 # Marginal tax brackets should be kept up to date.

    caTax = get_income_tax_from_brackets(taxable_income, _qcAbatement, _caBrackets)
    qcTax = get_income_tax_from_brackets(taxable_income, 0, _qcBrackets)
    total = caTax + qcTax
    return total
