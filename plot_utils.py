import matplotlib

def dollar_formatter():
    """
    Formatter that displays 2000 as $2,000
    """
    # https://stackoverflow.com/questions/38152356/matplotlib-dollar-sign-with-thousands-comma-tick-labels
    fmt = '${x:,.0f}'
    return matplotlib.ticker.StrMethodFormatter(fmt)