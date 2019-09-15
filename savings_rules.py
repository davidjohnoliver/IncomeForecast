import model

def get_simple_linear(initial_rrsp: float, final_rrsp: float, initial_year: int, career_length_yrs: int):
    """
    Sets the split between RRSP and TFSA as a linear function of time.

    s[y] = a + b*(y - y_0), where s = RRSP allotment (normalized), a = initial_rrsp (normalized value), 
                b = (final_rrsp - initial_rrsp) / career_length_yrs, y_0 = initial_year, y = current year
    """

    if not (0 <= initial_rrsp <= 1):
        raise ValueError("initial_rrsp must be between 0 and 1")

    if not (0 <= final_rrsp <= 1):
        raise ValueError("final_rrsp must be between 0 and 1")

    slope = (final_rrsp - initial_rrsp) / career_length_yrs # TODO: fix ensuing off-by-one errors

    def simple_linear(deltas: model.deltas_state, previous_funds: model.funds_state, previous_deltas: model.deltas_state):
        years_elapsed = deltas.year - initial_year

        if not (0 <= years_elapsed <= career_length_yrs):
            raise ValueError(f"{deltas.year} lies outside the allowed range of years for the rule (initial year={initial_year}, career length={career_length_yrs})")

        rrsp_norm = initial_rrsp + slope * years_elapsed        
        assert 0 <= rrsp_norm <= 1
        tfsa_norm = 1 - rrsp_norm

        output = deltas.update_rrsp(deltas.undifferentiated_savings * rrsp_norm)
        output = output.update_tfsa(deltas.undifferentiated_savings * tfsa_norm)

        return output
    
    return simple_linear