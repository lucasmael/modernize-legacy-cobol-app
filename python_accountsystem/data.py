class DataProgram:
    def __init__(self, initial_balance: float = 1000.00) -> None:
        self._storage_balance: float = float(initial_balance)

    def read(self) -> float:
        return float(self._storage_balance)

    def write(self, new_balance: float) -> None:
        self._storage_balance = float(new_balance)


