import solve
import math

class My_Intermediate:
    @property
    def my_float(self):
        return self._my_float
    @my_float.setter
    def my_float(self, value):
        self._my_float = value
    
    def __init__(self, myfloat):
        self._my_float = myfloat

def transform(input: float):
    return My_Intermediate(input)

def test_binary_solver():
    def model_fn(intermediate : My_Intermediate):
        x = intermediate.my_float
        return 2 * x - 7

    x_t, i_t = solve.binary_solver(transform, model_fn, 12, -100, 100, 0.00001)

    assert x_t == i_t.my_float
    assert math.isclose(9.5, x_t, rel_tol=0.0001)

def test_binary_solver_negative_slope():
    def model_fn(intermediate : My_Intermediate):
        x = intermediate.my_float
        return -3.6 * x + 19.2
    
    target = 44.7

    x_t, i_t = solve.binary_solver(transform, model_fn, target, -122, 217, 0.00001)

    assert x_t == i_t.my_float
    assert math.isclose(-7.08333333333, x_t, rel_tol=0.0001)