class Loop_Protection:
    def __init__(self) -> None:
        self._increments = 0

    def iterate(self):
        self._increments += 1
        if self._increments > 1000000:
            raise RuntimeError("Exceeded maximum loop iterations")
