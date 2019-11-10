
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
    :return: A tuple of (solution input, intermediate_fn(solution input), was_solution_found : bool)

    If no solution is found, the last calculated guess and intermediate product will be returned, with was_solution_found=false
    """
    if initial_lower_bound == initial_upper_bound:
        raise ValueError(f"Lower bound ({initial_lower_bound}) and upper bound ({initial_upper_bound}) are identical.")

    lower_bound_intermediate = intermediate_fn(initial_lower_bound)
    upper_bound_intermediate = intermediate_fn(initial_upper_bound)
    lower_bound_output = model_fn(lower_bound_intermediate)
    upper_bound_output = model_fn(upper_bound_intermediate)

    if lower_bound_output == upper_bound_output:
        raise ValueError("Model outputs are equal for lower and upper input bounds. The model function should be a non-flat monotonic function. ")

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
            return (guess, guess_intermediate, False)
        if guess_output > target_output:
            upper_guess = guess
        else:
            lower_guess = guess
    
    # We got a valid solution
    return (guess, guess_intermediate, True)