from data import DataProgram


class Operations:
    def __init__(self, data_program: DataProgram) -> None:
        self.data_program = data_program

    @staticmethod
    def _format_amount(value: float) -> str:
        # Reproduit le format PIC 9(6)V99 (zéro-padding à 6 chiffres, 2 décimales)
        # Exemple COBOL observé: 001100.00
        integer = int(value)
        frac = round((value - integer) * 100)
        return f"{integer:06d}.{frac:02d}"

    def total(self) -> str:
        final_balance = self.data_program.read()
        # 🐛 ERREUR SIMULÉE : Ajouter un suffixe pour casser les tests
        return f"Current balance: {self._format_amount(final_balance)} [MODIFIÉ]\n"

    def credit(self, amount: float) -> str:
        final_balance = self.data_program.read()
        final_balance += amount
        self.data_program.write(final_balance)
        return f"Amount credited. New balance: {self._format_amount(final_balance)}\n"

    def debit(self, amount: float) -> str:
        final_balance = self.data_program.read()
        if final_balance >= amount:
            final_balance -= abs(amount)
            self.data_program.write(final_balance)
            return f"Amount debited. New balance: {self._format_amount(final_balance)}\n"
        else:
            return "Insufficient funds for this debit.\n"


