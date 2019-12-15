import IPython.display

def with_colour(display_string : str, colour_string : str):
    return IPython.display.HTML(f'<text style="color: {colour_string}">{display_string}</text>')

def table(*headers):
    """
    Initializes a Markdown table. Takes the headers of the table as input
    
    :return: a table builder
    :rtype: Markdown_Table
    """
    return Markdown_Table(*headers)

class Markdown_Table:
    def __init__(self, *headers):
        self._separator = " | "
        self._str = self._separator.join(headers)
        self._columns = len(headers)
        dividers = ["---" for h in headers]
        self.append_row(*dividers)
    
    def append_row(self, *row_entries):
        """
        Appends a row of entries to the current table. The number of entries must match the number of columns (defined by the number of 
        headers initially provided.)
        :return: The table builder, for fluent chaining
        """
        if (self._columns != len(row_entries)):
            raise ValueError(f"Table has {self._columns} columns but only {len(row_entries)} entries were provided")

        self._str = self._str + "\n"
        self._str = self._str + self._separator.join(row_entries)

        return self #Permit fluent chaining
    
    def close(self):
        """
        Completes the table and returns a displayable Markdown object
        """
        return IPython.display.Markdown(self._str)