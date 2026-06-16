import tax
import math
import datetime

def test_get_income_tax():
    correct_answers = [ #Calculated at https://www.calculconversion.com/income-tax-calculator-quebec.html and https://www.taxtips.ca/calculators/enhanced-basic/basic-tax-calculator.htm
        (10000, 0),
        (20000, 561),
        (30000, 3130),
        (50000, 8268),
        (70000, 14812),
        (90000, 22036),
        (110000, 29325),
        (150000, 47596),
        (200000, 71837),
        (250000, 96943),
    ]

    assert datetime.datetime.now().year == 2026 # These values have an expiry date

    for pair in correct_answers:
        expected = pair[1]
        actual = tax.get_income_tax(pair[0])
        assert math.isclose(expected, actual, abs_tol=2)
