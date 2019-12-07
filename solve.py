from typing import Callable
import scipy.optimize

def binary_solver(intermediate_fn, model_fn, target_output : float, initial_lower_bound : float, initial_upper_bound : float, tolerance : float):
    """
    Solver which finds the input which produces the supplied target output, using a simple binary search-like algorithm.
    
    :param intermediate_fn: Intermediate transformation function, which takes a single input float and returns an object of any type
    :param model_fn: Model function, which takes the product of intermediate_fn as its input, and produces a double as output. This is 
        assumed to be a monotonic function of the input.
    :param target_output: The target output from model_fn
    :type target_output: float
    :param initial_lower_bound: A lower bound on the allowable input values
    :type initial_lower_bound: float
    :param initial_upper_bound: An upper bound on the allowable input values
    :type initial_upper_bound: float
    :param tolerance: The allowable deviation from the target and final calculated output
    :type tolerance: float
    :return: A tuple of (solution input, intermediate_fn(solution input), was_solution_found : bool, message : str)

    If no solution is found, the last calculated guess and intermediate product will be returned, with was_solution_found=false
    """
    if initial_lower_bound == initial_upper_bound:
        return (None, None, False, f"Lower bound ({initial_lower_bound}) and upper bound ({initial_upper_bound}) are identical.")

    lower_bound_intermediate = intermediate_fn(initial_lower_bound)
    upper_bound_intermediate = intermediate_fn(initial_upper_bound)
    lower_bound_output = model_fn(lower_bound_intermediate)
    upper_bound_output = model_fn(upper_bound_intermediate)

    if lower_bound_output == upper_bound_output:
        return (initial_lower_bound, lower_bound_intermediate, False, "Model outputs are equal for lower and upper input bounds. The model function should be a non-flat monotonic function. ")

    lower_guess = 0
    upper_guess = 0

    if upper_bound_output > lower_bound_output:
        lower_guess = initial_lower_bound
        upper_guess = initial_upper_bound
    else:
        lower_guess = initial_upper_bound
        upper_guess = initial_lower_bound
    
    guess_output = float('-inf')
    guess = 0
    guess_intermediate = None

    eps = tolerance * 1e-5

    while abs(guess_output - target_output) > tolerance:
        guess = (lower_guess + upper_guess) / 2
        guess_intermediate = intermediate_fn(guess)
        guess_output = model_fn(guess_intermediate)
        if abs(lower_guess - upper_guess) < eps:
            # No solution found, return the last thing we got
            return (guess, guess_intermediate, False, "Exhausted value range and no solution found")
        if guess_output > target_output:
            upper_guess = guess
        else:
            lower_guess = guess
    
    # We got a valid solution
    return (guess, guess_intermediate, True, "Success")

class Optimizing_Solver:
    """
    Wraps a simulation solver and allows any number of variables to be optimized (for minimum initial input).
    """
    
    PENALTY_BASE = 1e30

    def __init__(self, inner_solver, should_invert : bool):
        self._inner_solver = inner_solver
        self._should_invert = should_invert

        self._variable_names = []
        self._bounds = []
        self._x0 = []
        self._x = []
        self._x_sol = []
        self._optimize_values = 0
        self._output = ()

    def subscribe_optimized_scalar(self, variable_name : str, lower_bound : float = None, upper_bound : float = None, initial_guess : float = None) -> Callable[[], float]:
        """
        Registers a variable to be optimized.
        
        :param variable_name: An identifier for the variable to be optimized.
        :type variable_name: str
        :param lower_bound: An optional lower bound for the variable, defaults to None
        :type lower_bound: float, optional
        :param upper_bound: An optional upper bound for the variable, defaults to None
        :type upper_bound: float, optional
        :param initial_guess: An optional initial guess for the variable - if this is not supplied, the average of lower and upper bounds will be used, defaults to None
        :type initial_guess: float, optional
        :return: A function that returns the current guess for the variable.
        :rtype: Callable[[], float]
        """
        self._variable_names.append(variable_name)
        self._bounds.append((lower_bound, upper_bound))
        x0 = initial_guess if initial_guess is not None else (lower_bound + upper_bound) / 2.0
        self._x0.append(x0)
        i = self._optimize_values
        self._optimize_values +=1
        return lambda: self._x[i]
    
    def get_optimized_value(self, variable_name : str):
        """
        Gets the optimum value found for the named variable.
        
        :param variable_name: Variable name
        :type variable_name: str
        :return: Optimized value
        :rtype: [type]
        """
        i = self._variable_names.index(variable_name)
        return self._x_sol[i]
    
    def get_all_optimized_values(self):
        """
        Returns a sequence of (variable_name, optimized_value) pairs for all optimized variables
        """

        return ((self._variable_names[i], self._x_sol[i]) for i in range(0, self._optimize_values))
    
    def set_failed(self):
        """
        When called by an optimizable routine, indicates that the routine has reached an invalid state that shouldn't be counted as a solution.
        """
        self._did_fail = True

    @property
    def initial_output(self):
        """Returns output for the first valid solution found, for comparison with the final optimized solution."""
        return self._output_initial
        
    def get_all_initial_solution_values(self):
        """
        Returns a sequence of (variable_name, optimized_value) pairs for all un-optimized variables corresponding to the first valid solution
        """

        return ((self._variable_names[i], self._x_initial[i]) for i in range(0, self._optimize_values))

    
    def solve(self, intermediate_fn, model_fn, target_output : float, initial_lower_bound : float, initial_upper_bound : float, tolerance : float):
        if (self._optimize_values == 0):
            # In the trivial case that no optimized values have been requested, just return the result of the inner solver
            return self._inner_solver(intermediate_fn, model_fn, target_output, initial_lower_bound, initial_upper_bound, tolerance)

        self._has_initial_solution = False
        
        def minimize_func(x):
            self._x = x
            self._did_fail = False
            self._output = self._inner_solver(intermediate_fn, model_fn, target_output, initial_lower_bound, initial_upper_bound, tolerance)
            f = self._output[0]
            f = self._apply_soft_bounds(f, x)
            if (not self._output[2] or self._did_fail):
                # Penalize invalid solution, so that optimizer doesn't try to use it
                f += self.PENALTY_BASE
            elif not self._has_initial_solution:
                #
                self._has_initial_solution = True

                self._output_initial = self._output
                self._x_initial = x
            
            return -f if self._should_invert else f
        
        opt_result = scipy.optimize.minimize(minimize_func, self._x0, method='Nelder-Mead', tol = tolerance) 
        # Nelder-Mead is robust to non-smooth functions, which is important because the output of the inner solver tends to be 'staircase-like' 
        # unless the tolerance is very precise, resulting in the initial guess being returned as answer
        # See eg https://stackoverflow.com/questions/36110998/why-does-scipy-optimize-minimize-default-report-success-without-moving-with-sk

        self._x_sol = opt_result.x

        output = self._output
        return (output[0], output[1], output[2] and opt_result.success, output[3])
    
    def _apply_soft_bounds(self, f : float, x):
        """
        Apply 'soft' bounds to the objective function, since the Nelder-Mead method doesn't support true bounds.
        """
        for i in range(0, len(x)):
            bnds = self._bounds[i]
            v = x[i]

            lower_bound = bnds[0]
            if (lower_bound is not None and v < lower_bound):
                diff = lower_bound - v
                f += self.PENALTY_BASE + 100 * diff
        
            upper_bound = bnds[1]
            if (upper_bound is not None and v > upper_bound):
                diff = v - upper_bound
                f += self.PENALTY_BASE + 100 * diff

        return f