class HistoricValue:
    """
    Keeps a record of a value over a time period.
    """

    @property
    def initial_year(self):
        return self._initial_year

    @property
    def latest_year(self):
        return self._initial_year + len(self._values) - 1

    @property
    def values(self):
        return tuple(self._values)


    def __init__(self, initial_value: float, initial_year: int):
        self._values = [ initial_value]
        self._initial_year = initial_year

    def set_latest_value(self, value : float):
        self._values.append(value)