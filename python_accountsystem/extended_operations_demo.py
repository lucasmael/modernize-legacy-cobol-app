#!/usr/bin/env python3
"""
Démonstration de l'architecture extensible des opérations
Montre comment ajouter facilement de nouvelles opérations
"""

import sys
import os
from data import DataProgram
from operations import (
    Operations, OperationType, BaseOperation, OperationResult, ViewBalanceOperation
)

# Ajouter le répertoire parent pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'python_accountsystem'))


class InterestOperation(BaseOperation):
    """Exemple d'opération personnalisée : calcul d'intérêts."""
    
    def __init__(self, data_program, interest_rate: float = 0.02):
        super().__init__(data_program)
        self.interest_rate = interest_rate
    
    def execute(self, amount=None) -> OperationResult:
        current_balance = self.data_program.read()
        
        if current_balance <= 0:
            return OperationResult(False, "No interest on zero or negative balance.\n")
        
        interest = current_balance * self.interest_rate
        new_balance = current_balance + interest
        self.data_program.write(new_balance)
        
        message = (f"Interest applied ({self.interest_rate:.1%}): "
                  f"{self._format_amount(interest)}\n"
                  f"New balance: {self._format_amount(new_balance)}\n")
        
        return OperationResult(True, message, new_balance)
    
    def get_operation_type(self) -> OperationType:
        # Pour cet exemple, on étend l'enum temporairement
        return "INTEREST"  # En production, étendre OperationType


class FeesOperation(BaseOperation):
    """Exemple d'opération personnalisée : frais de gestion."""
    
    def __init__(self, data_program, fee_amount: float = 5.00):
        super().__init__(data_program)
        self.fee_amount = fee_amount
    
    def execute(self, amount=None) -> OperationResult:
        current_balance = self.data_program.read()
        
        if current_balance < self.fee_amount:
            return OperationResult(False, f"Insufficient funds for fee: {self._format_amount(self.fee_amount)}\n")
        
        new_balance = current_balance - self.fee_amount
        self.data_program.write(new_balance)
        
        message = (f"Management fee deducted: {self._format_amount(self.fee_amount)}\n"
                  f"New balance: {self._format_amount(new_balance)}\n")
        
        return OperationResult(True, message, new_balance)
    
    def get_operation_type(self) -> OperationType:
        return "FEES"  # En production, étendre OperationType


def demo_basic_operations():
    """Démonstration des opérations de base."""
    print("🏦 DÉMONSTRATION - OPÉRATIONS DE BASE")
    print("=" * 50)
    
    # Initialisation
    data = DataProgram(initial_balance=1000.00)
    ops = Operations(data)
    
    print(f"Solde initial: {ViewBalanceOperation._format_amount(data.read())}")
    
    # Test des opérations via la nouvelle API
    operations_to_test = [
        (OperationType.VIEW_BALANCE, None, "Affichage du solde"),
        (OperationType.CREDIT, 250.00, "Crédit de 250.00"),
        (OperationType.VIEW_BALANCE, None, "Vérification après crédit"),
        (OperationType.DEBIT, 150.00, "Débit de 150.00"),
        (OperationType.DEBIT, 2000.00, "Débit insuffisant (erreur attendue)"),
        (OperationType.VIEW_BALANCE, None, "Solde final"),
    ]
    
    for operation_type, amount, description in operations_to_test:
        print(f"\n🔹 {description}")
        result = ops.execute_operation(operation_type, amount)
        print(f"   Résultat: {'✅' if result.success else '❌'} {result.message.strip()}")


def demo_extended_operations():
    """Démonstration des opérations étendues."""
    print("\n\n🚀 DÉMONSTRATION - OPÉRATIONS ÉTENDUES")
    print("=" * 50)
    
    # Initialisation
    data = DataProgram(initial_balance=1500.00)
    ops = Operations(data)
    
    print(f"Solde initial: {ViewBalanceOperation._format_amount(data.read())}")
    
    # Enregistrement de nouvelles opérations
    print("\n🔧 Enregistrement de nouvelles opérations...")
    ops.register_operation("INTEREST", lambda: InterestOperation(data, 0.025))  # 2.5%
    ops.register_operation("FEES", lambda: FeesOperation(data, 10.00))          # 10€ de frais
    
    # Test des nouvelles opérations
    extended_operations = [
        ("INTEREST", None, "Application d'intérêts (2.5%)"),
        ("FEES", None, "Prélèvement frais de gestion (10€)"),
        (OperationType.VIEW_BALANCE, None, "Solde après opérations étendues"),
    ]
    
    for operation_type, amount, description in extended_operations:
        print(f"\n🔹 {description}")
        result = ops.execute_operation(operation_type, amount)
        print(f"   Résultat: {'✅' if result.success else '❌'} {result.message.strip()}")


def demo_operations_registry():
    """Démonstration du registre d'opérations."""
    print("\n\n📋 DÉMONSTRATION - REGISTRE D'OPÉRATIONS")
    print("=" * 50)
    
    data = DataProgram()
    ops = Operations(data)
    
    print("Opérations disponibles par défaut:")
    for op_type, description in ops.get_available_operations().items():
        status = "✅ Implémentée" if op_type in [OperationType.VIEW_BALANCE, OperationType.CREDIT, OperationType.DEBIT] else "🚧 Future"
        print(f"  {op_type.value:15} - {description} ({status})")
    
    # Ajout d'opérations personnalisées
    print("\nAjout d'opérations personnalisées:")
    ops.register_operation("INTEREST", lambda: InterestOperation(data))
    ops.register_operation("FEES", lambda: FeesOperation(data))
    
    print("  INTEREST        - Calculate and apply interest (✅ Ajoutée)")
    print("  FEES            - Apply management fees (✅ Ajoutée)")


def demo_compatibility():
    """Démonstration de la compatibilité avec l'ancienne API."""
    print("\n\n🔄 DÉMONSTRATION - COMPATIBILITÉ ANCIENNE API")
    print("=" * 50)
    
    data = DataProgram(initial_balance=800.00)
    ops = Operations(data)
    
    print("Utilisation de l'ancienne API (100% compatible):")
    
    # L'ancien code continue de fonctionner
    print(f"🔹 Ancienne méthode: {ops.total().strip()}")
    print(f"🔹 Ancienne méthode: {ops.credit(200.00).strip()}")
    print(f"🔹 Ancienne méthode: {ops.debit(50.00).strip()}")
    print(f"🔹 Ancienne méthode: {ops.total().strip()}")


def demo_error_handling():
    """Démonstration de la gestion d'erreurs."""
    print("\n\n⚠️  DÉMONSTRATION - GESTION D'ERREURS")
    print("=" * 50)
    
    data = DataProgram(initial_balance=100.00)
    ops = Operations(data)
    
    error_cases = [
        (OperationType.CREDIT, -50.00, "Crédit négatif"),
        (OperationType.DEBIT, -25.00, "Débit négatif"),
        (OperationType.DEBIT, 500.00, "Débit supérieur au solde"),
        ("UNKNOWN_OP", 100.00, "Opération inconnue"),
    ]
    
    for operation_type, amount, description in error_cases:
        print(f"\n🔹 Test: {description}")
        result = ops.execute_operation(operation_type, amount)
        print(f"   Résultat: {'✅' if result.success else '❌'} {result.message.strip()}")


def main():
    """Fonction principale de démonstration."""
    print("🏦 ARCHITECTURE EXTENSIBLE DES OPÉRATIONS")
    print("=" * 60)
    print("Démonstration des améliorations architecturales\n")
    
    try:
        demo_basic_operations()
        demo_extended_operations() 
        demo_operations_registry()
        demo_compatibility()
        demo_error_handling()
        
        print("\n\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS")
        print("=" * 60)
        print("✅ Architecture flexible et extensible")
        print("✅ Compatibilité avec l'API existante")
        print("✅ Gestion d'erreurs robuste")
        print("✅ Facilité d'ajout de nouvelles opérations")
        
    except Exception as e:
        print(f"\n❌ Erreur pendant la démonstration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
