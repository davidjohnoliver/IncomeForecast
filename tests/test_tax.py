import tax
import math
import datetime

def test_get_income_tax():
    correct_answers = [ #Calculated at https://www.taxtips.ca/calculators/basic/basic-tax-calculator.htm
        (10000, 0),
        (20000, 1416),
        (30000, 4169),
        (50000, 9964),
        (70000, 17387),
        (90000, 24811),
        (110000, 33580),
        (150000, 52564),
        (200000, 77626),
        (250000, 103771),
    ]

    assert datetime.datetime.now().year == 2021 # These values have an expiry date

    for pair in correct_answers:
        expected = pair[1]
        actual = tax.get_income_tax(pair[0])
        assert math.isclose(expected, actual, abs_tol=2)