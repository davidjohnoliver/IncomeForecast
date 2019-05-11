import tax
import math
import datetime

def test_get_income_tax():
    correct_answers = [ #Calculated at http://www.calculconversion.com/income-tax-calculator-quebec.html
        (10000, 0),
        (20000, 1703.01),
        (30000, 4455.51),
        (50000, 10379.85),
        (70000, 17803.35),
        (90000, 25323.84),
        (110000, 34284.61),
        (150000, 53327.04),
        (200000, 78309.54),
        (250000, 104615.65),
    ]

    assert datetime.datetime.now().year == 2019 # These values have an expiry date

    for pair in correct_answers:
        expected = pair[1]
        actual = tax.get_income_tax(pair[0])
        assert math.isclose(expected, actual, abs_tol=0.01)