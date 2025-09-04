#!/usr/bin/env python3
"""
Tests Golden Master pour vérifier que le programme Python produit
la même sortie que le programme COBOL original.

Ce script compare les fichiers approved (générés par COBOL) avec
les fichiers received (générés par Python) pour chaque cas de test.
"""

import os
import subprocess
import sys
import unittest
from typing import Dict, List


# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "inputs")
APPROVED_DIR = os.path.join(PROJECT_ROOT, "tests", "approved")
RECEIVED_DIR = os.path.join(PROJECT_ROOT, "tests", "received")
PYTHON_MAIN = os.path.join(PROJECT_ROOT, "python_accountsystem", "main.py")


def run_python_program(input_text: str) -> str:
    """Exécute le programme Python avec l'entrée fournie et renvoie la sortie stdout."""
    result = subprocess.run(
        [sys.executable, PYTHON_MAIN],
        input=input_text.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Erreur d'exécution Python: {result.stderr.decode(errors='replace')}")

    return result.stdout.decode(errors="replace")


def get_test_cases_from_inputs() -> List[Dict[str, str]]:
    """Lit les fichiers d'entrée existants pour générer les cas de test."""
    cases = []
    
    if not os.path.exists(INPUT_DIR):
        return cases
    
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.in'):
            case_id = filename[:-3]  # Enlever l'extension .in
            input_path = os.path.join(INPUT_DIR, filename)
            
            with open(input_path, "r", encoding="utf-8") as f:
                input_text = f.read()
            
            cases.append({
                "id": case_id,
                "input": input_text
            })
    
    return sorted(cases, key=lambda x: x["id"])


def ensure_received_dir():
    """S'assure que le répertoire received existe."""
    os.makedirs(RECEIVED_DIR, exist_ok=True)


class TestGoldenMaster(unittest.TestCase):
    """Tests Golden Master comparant les sorties COBOL (approved) et Python (received)."""
    
    @classmethod
    def setUpClass(cls):
        """Configuration avant tous les tests."""
        ensure_received_dir()
        
        # Générer tous les fichiers received en une fois
        cases = get_test_cases_from_inputs()
        for case in cases:
            case_id = case["id"]
            input_text = case["input"]
            
            try:
                output = run_python_program(input_text)
                received_path = os.path.join(RECEIVED_DIR, f"{case_id}.received.txt")
                with open(received_path, "w", encoding="utf-8") as f:
                    f.write(output)
            except Exception as exc:
                raise RuntimeError(f"Impossible de générer received pour {case_id}: {exc}")
    
    def test_tc_1_1_view_balance(self):
        """TC-1.1: View Current Balance"""
        self._compare_outputs("TC-1.1")
    
    def test_tc_2_1_credit_valid_amount(self):
        """TC-2.1: Credit Account with Valid Amount"""
        self._compare_outputs("TC-2.1")
    
    def test_tc_2_2_credit_zero_amount(self):
        """TC-2.2: Credit Account with Zero Amount"""
        self._compare_outputs("TC-2.2")
    
    def test_tc_3_1_debit_valid_amount(self):
        """TC-3.1: Debit Account with Valid Amount"""
        self._compare_outputs("TC-3.1")
    
    def test_tc_3_2_debit_insufficient_funds(self):
        """TC-3.2: Debit Account with Amount Greater Than Balance"""
        self._compare_outputs("TC-3.2")
    
    def test_tc_3_3_debit_zero_amount(self):
        """TC-3.3: Debit Account with Zero Amount"""
        self._compare_outputs("TC-3.3")
    
    def test_tc_4_1_exit_application(self):
        """TC-4.1: Exit the Application"""
        self._compare_outputs("TC-4.1")
    
    def _compare_outputs(self, case_id: str):
        """Compare la sortie approved avec la sortie received pour un cas de test."""
        approved_path = os.path.join(APPROVED_DIR, f"{case_id}.approved.txt")
        received_path = os.path.join(RECEIVED_DIR, f"{case_id}.received.txt")
        
        # Vérifier que les fichiers existent
        self.assertTrue(os.path.exists(approved_path), 
                       f"Fichier approved manquant: {approved_path}")
        self.assertTrue(os.path.exists(received_path), 
                       f"Fichier received manquant: {received_path}")
        
        # Lire les contenus
        with open(approved_path, "r", encoding="utf-8") as f:
            approved_content = f.read()
        
        with open(received_path, "r", encoding="utf-8") as f:
            received_content = f.read()
        
        # Comparer les contenus
        if approved_content != received_content:
            # Afficher les différences pour le debug
            self._show_diff(case_id, approved_content, received_content)
        
        self.assertEqual(approved_content, received_content, 
                        f"Différence détectée pour {case_id}")
    
    def _show_diff(self, case_id: str, approved: str, received: str):
        """Affiche les différences entre approved et received."""
        print(f"\n{'='*50}")
        print(f"DIFFÉRENCES POUR {case_id}")
        print(f"{'='*50}")
        
        approved_lines = approved.splitlines()
        received_lines = received.splitlines()
        
        print("APPROVED:")
        for i, line in enumerate(approved_lines, 1):
            print(f"{i:2d}: {repr(line)}")
        
        print("\nRECEIVED:")
        for i, line in enumerate(received_lines, 1):
            print(f"{i:2d}: {repr(line)}")
        
        print(f"{'='*50}")


class TestBulkGoldenMaster(unittest.TestCase):
    """Test en lot pour tous les cas de test Golden Master."""
    
    def test_all_cases_match_golden_master(self):
        """Vérifie que tous les cas de test Python correspondent aux Golden Masters COBOL."""
        ensure_received_dir()
        cases = get_test_cases_from_inputs()
        
        if not cases:
            self.skipTest("Aucun cas de test trouvé")
        
        results = []
        
        for case in cases:
            case_id = case["id"]
            input_text = case["input"]
            
            # Générer la sortie du programme Python
            try:
                received_output = run_python_program(input_text)
            except Exception as exc:
                results.append(f"❌ {case_id}: Erreur d'exécution - {exc}")
                continue
            
            # Sauvegarder le fichier received
            received_path = os.path.join(RECEIVED_DIR, f"{case_id}.received.txt")
            with open(received_path, "w", encoding="utf-8") as f:
                f.write(received_output)
            
            # Lire le fichier approved correspondant
            approved_path = os.path.join(APPROVED_DIR, f"{case_id}.approved.txt")
            if not os.path.exists(approved_path):
                results.append(f"⚠️  {case_id}: Fichier approved manquant")
                continue
            
            with open(approved_path, "r", encoding="utf-8") as f:
                approved_output = f.read()
            
            # Comparer les sorties
            if received_output == approved_output:
                results.append(f"✅ {case_id}: CORRESPONDANCE PARFAITE")
            else:
                results.append(f"❌ {case_id}: DIFFÉRENCE DÉTECTÉE")
        
        # Afficher les résultats
        print("\n" + "="*60)
        print("RÉSULTATS DES TESTS GOLDEN MASTER")
        print("="*60)
        for result in results:
            print(result)
        print("="*60)
        
        # Compter les succès
        success_count = len([r for r in results if r.startswith("✅")])
        total_count = len(results)
        
        print(f"\nRésumé: {success_count}/{total_count} tests réussis")
        
        # Vérifier qu'aucun cas n'a échoué
        failed_cases = [r for r in results if r.startswith("❌")]
        if failed_cases:
            self.fail(f"{len(failed_cases)} cas de test ont échoué:\n" + "\n".join(failed_cases))
        
        print("🎉 TOUS LES TESTS GOLDEN MASTER ONT RÉUSSI!")


if __name__ == "__main__":
    print("🧪 Lancement des tests Golden Master")
    print("Comparaison entre les sorties COBOL (approved) et Python (received)")
    print("="*70)
    
    unittest.main(verbosity=2)
