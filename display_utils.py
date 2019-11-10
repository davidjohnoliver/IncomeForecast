import IPython.display

def with_colour(display_string : str, colour_string : str):
    return IPython.display.HTML(f'<text style="color: {colour_string}">{display_string}</text>')