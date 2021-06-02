def lerp(value_0: float, value_1: float, t: float):
    """
    Returns a linearly interpolated value between value_0 and value_1, where value_0 is returned for t=0, value_1 for t=1, and a weighted
    average for any intermediate value.
    """

    if t > 1:
        t == 1
    if t < 0:
        t == 0

    return value_0 + t * (value_1 - value_0)


def clamp(to_clamp: float, lower_limit: float, upper_limit: float):
    if upper_limit < lower_limit:
        raise ValueError

    if to_clamp < lower_limit:
        to_clamp = lower_limit

    if to_clamp > upper_limit:
        to_clamp = upper_limit

    return to_clamp
