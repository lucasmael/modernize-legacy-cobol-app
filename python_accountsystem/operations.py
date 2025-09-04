from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Callable, Optional
from data import DataProgram


class OperationType(Enum):
    """Énumération des types d'opérations disponibles."""
    VIEW_BALANCE = "view_balance"
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"  # Exemple d'extension future
    HISTORY = "history"    # Exemple d'extension future


class OperationResult:
    """Résultat d'une opération avec métadonnées."""
    
    def __init__(self, success: bool, message: str, new_balance: Optional[float] = None):
        self.success = success
        self.message = message
        self.new_balance = new_balance
        
    def __str__(self) -> str:
        return self.message


class BaseOperation(ABC):
    """Classe de base pour toutes les opérations."""
    
    def __init__(self, data_program: DataProgram):
        self.data_program = data_program
    
    @staticmethod
    def _format_amount(value: float) -> str:
        """Reproduit le format PIC 9(6)V99 (zéro-padding à 6 chiffres, 2 décimales)."""
        # Exemple COBOL observé: 001100.00
        integer = int(value)
        frac = round((value - integer) * 100)
        return f"{integer:06d}.{frac:02d}"
    
    @abstractmethod
    def execute(self, amount: Optional[float] = None) -> OperationResult:
        """Exécute l'opération."""
        pass
    
    @abstractmethod
    def get_operation_type(self) -> OperationType:
        """Retourne le type d'opération."""
        pass


class ViewBalanceOperation(BaseOperation):
    """Opération d'affichage du solde."""
    
    def execute(self, amount: Optional[float] = None) -> OperationResult:
        current_balance = self.data_program.read()
        message = f"Current balance: {self._format_amount(current_balance)}\n"
        return OperationResult(True, message, current_balance)
    
    def get_operation_type(self) -> OperationType:
        return OperationType.VIEW_BALANCE


class CreditOperation(BaseOperation):
    """Opération de crédit."""
    
    def execute(self, amount: Optional[float] = None) -> OperationResult:
        if amount is None:
            return OperationResult(False, "Amount required for credit operation.\n")
        
        if amount < 0:
            return OperationResult(False, "Credit amount must be positive.\n")
        
        current_balance = self.data_program.read()
        new_balance = current_balance + amount
        self.data_program.write(new_balance)
        
        message = f"Amount credited. New balance: {self._format_amount(new_balance)}\n"
        return OperationResult(True, message, new_balance)
    
    def get_operation_type(self) -> OperationType:
        return OperationType.CREDIT


class DebitOperation(BaseOperation):
    """Opération de débit."""
    
    def execute(self, amount: Optional[float] = None) -> OperationResult:
        if amount is None:
            return OperationResult(False, "Amount required for debit operation.\n")
        
        if amount < 0:
            return OperationResult(False, "Debit amount must be positive.\n")
        
        current_balance = self.data_program.read()
        
        if current_balance >= amount:
            new_balance = current_balance - abs(amount)
            self.data_program.write(new_balance)
            message = f"Amount debited. New balance: {self._format_amount(new_balance)}\n"
            return OperationResult(True, message, new_balance)
        else:
            return OperationResult(False, "Insufficient funds for this debit.\n", current_balance)
    
    def get_operation_type(self) -> OperationType:
        return OperationType.DEBIT


class TransferOperation(BaseOperation):
    """Opération de transfert (exemple d'extension future)."""
    
    def execute(self, amount: Optional[float] = None) -> OperationResult:
        # Implémentation future pour les transferts
        return OperationResult(False, "Transfer operation not yet implemented.\n")
    
    def get_operation_type(self) -> OperationType:
        return OperationType.TRANSFER


class HistoryOperation(BaseOperation):
    """Opération d'historique (exemple d'extension future)."""
    
    def execute(self, amount: Optional[float] = None) -> OperationResult:
        # Implémentation future pour l'historique
        return OperationResult(False, "History operation not yet implemented.\n")
    
    def get_operation_type(self) -> OperationType:
        return OperationType.HISTORY


class Operations:
    """Gestionnaire d'opérations avec pattern Strategy et switch extensible."""
    
    def __init__(self, data_program: DataProgram) -> None:
        self.data_program = data_program
        
        # Registry des opérations disponibles
        self._operations: Dict[OperationType, Callable[[], BaseOperation]] = {
            OperationType.VIEW_BALANCE: lambda: ViewBalanceOperation(self.data_program),
            OperationType.CREDIT: lambda: CreditOperation(self.data_program),
            OperationType.DEBIT: lambda: DebitOperation(self.data_program),
            OperationType.TRANSFER: lambda: TransferOperation(self.data_program),
            OperationType.HISTORY: lambda: HistoryOperation(self.data_program),
        }
    
    def execute_operation(self, operation_type: OperationType, amount: Optional[float] = None) -> OperationResult:
        """Exécute une opération basée sur son type."""
        if operation_type not in self._operations:
            return OperationResult(False, f"Unknown operation type: {operation_type}\n")
        
        operation = self._operations[operation_type]()
        return operation.execute(amount)
    
    def get_available_operations(self) -> Dict[OperationType, str]:
        """Retourne la liste des opérations disponibles."""
        return {
            OperationType.VIEW_BALANCE: "View account balance",
            OperationType.CREDIT: "Credit account",
            OperationType.DEBIT: "Debit account", 
            OperationType.TRANSFER: "Transfer funds (future)",
            OperationType.HISTORY: "View transaction history (future)",
        }
    
    def register_operation(self, operation_type: OperationType, operation_factory: Callable[[], BaseOperation]) -> None:
        """Permet d'enregistrer de nouvelles opérations dynamiquement."""
        self._operations[operation_type] = operation_factory
    
    # === Méthodes de compatibilité avec l'ancienne API ===
    
    def total(self) -> str:
        """Méthode de compatibilité pour l'ancienne API."""
        result = self.execute_operation(OperationType.VIEW_BALANCE)
        return str(result)
    
    def credit(self, amount: float) -> str:
        """Méthode de compatibilité pour l'ancienne API."""
        result = self.execute_operation(OperationType.CREDIT, amount)
        return str(result)
    
    def debit(self, amount: float) -> str:
        """Méthode de compatibilité pour l'ancienne API."""
        result = self.execute_operation(OperationType.DEBIT, amount)
        return str(result)


