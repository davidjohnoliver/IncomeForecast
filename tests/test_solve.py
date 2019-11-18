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

    x_t, i_t, s_t = solve.binary_solver(transform, model_fn, 12, -100, 100, 0.00001)

    assert x_t == i_t.my_float
    assert math.isclose(9.5, x_t, rel_tol=0.0001)
    assert s_t

def test_binary_solver_negative_slope():
    def model_fn(intermediate : My_Intermediate):
        x = intermediate.my_float
        return -3.6 * x + 19.2
    
    target = 44.7

    x_t, i_t, s_t = solve.binary_solver(transform, model_fn, target, -122, 217, 0.00001)

    assert x_t == i_t.my_float
    assert math.isclose(-7.08333333333, x_t, rel_tol=0.0001)
    assert s_t

def test_optimizing_solver_no_optimized_value():
    def model_fn(intermediate : My_Intermediate):
        x = intermediate.my_float
        return 2 * x - 7

    opt = solve.Optimizing_Solver(solve.binary_solver)

    x_t, i_t, s_t = opt.solve(transform, model_fn, 12, -100, 100, 0.00001)

    assert x_t == i_t.my_float
    assert math.isclose(9.5, x_t, rel_tol=0.0001)
    assert s_t

def test_optimizing_solver():
    opt = solve.Optimizing_Solver(solve.binary_solver)

    optimized_scalar1 = opt.subscribe_optimized_scalar("Rugosity", lower_bound=-20, upper_bound=10)
    optimized_scalar2 = opt.subscribe_optimized_scalar("Tripticity", lower_bound=-90, upper_bound=-5)

    def model_fn(intermediate : My_Intermediate):
        x = intermediate.my_float
        r = optimized_scalar1()
        t = optimized_scalar2()
        return 2 * x - 7 - abs(r - 3.1)  - abs (t + 8.5)


    x_t, i_t, s_t = opt.solve(transform, model_fn, 12, -100, 100, 1e-5)

    assert x_t == i_t.my_float
    assert math.isclose(9.5, x_t, rel_tol=0.0001)
    assert s_t
    assert math.isclose(3.1, opt.get_optimized_value("Rugosity"), rel_tol=0.0001)
    assert math.isclose(-8.5, opt.get_optimized_value("Tripticity"), rel_tol=0.0001)

def test_optimizing_solver_bounded():
    opt = solve.Optimizing_Solver(solve.binary_solver)

    optimized_scalar1 = opt.subscribe_optimized_scalar("Rugosity", lower_bound=-20, upper_bound=10)
    optimized_scalar2 = opt.subscribe_optimized_scalar("Tripticity", lower_bound=-90, upper_bound=-10.3)

    def model_fn(intermediate : My_Intermediate):
        x = intermediate.my_float
        r = optimized_scalar1()
        t = optimized_scalar2()
        return 2 * x - 7 - abs(r - 3.1)  - abs (t + 8.5)


    x_t, i_t, s_t = opt.solve(transform, model_fn, 12, -100, 100, 1e-5)

    assert x_t == i_t.my_float
    assert math.isclose(10.4, x_t, rel_tol=0.0001) # t = -10.3, 2x - 7 - (10.3 - 8.5) = 12, 2x = 20.8, x = 10.4
    assert s_t
    assert math.isclose(3.1, opt.get_optimized_value("Rugosity"), rel_tol=0.0001)
    assert math.isclose(-10.3, opt.get_optimized_value("Tripticity"), rel_tol=0.0001)