import os
import subprocess
import sys
import unittest
from typing import Dict, List

# Ajouter le répertoire parent au path pour importer approvaltests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from approvaltests import verify
    from approvaltests.reporters import PythonNativeReporter
except ImportError:
    print("❌ ApprovalTests n'est pas installé. Installez-le avec: pip install approvaltests")
    sys.exit(1)


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


class TestPythonAccountSystem(unittest.TestCase):
    
    def setUp(self):
        """Configuration avant chaque test."""
        os.makedirs(RECEIVED_DIR, exist_ok=True)
    
    def test_tc_1_1_view_balance(self):
        """TC-1.1: View Current Balance"""
        input_text = "1\n4\n"
        output = run_python_program(input_text)
        verify(output, reporter=PythonNativeReporter())
    
    def test_tc_2_1_credit_valid_amount(self):
        """TC-2.1: Credit Account with Valid Amount"""
        input_text = "2\n100.00\n4\n"
        output = run_python_program(input_text)
        verify(output, reporter=PythonNativeReporter())
    
    def test_tc_2_2_credit_zero_amount(self):
        """TC-2.2: Credit Account with Zero Amount"""
        input_text = "2\n0.00\n4\n"
        output = run_python_program(input_text)
        verify(output, reporter=PythonNativeReporter())
    
    def test_tc_3_1_debit_valid_amount(self):
        """TC-3.1: Debit Account with Valid Amount"""
        input_text = "3\n50.00\n4\n"
        output = run_python_program(input_text)
        verify(output, reporter=PythonNativeReporter())
    
    def test_tc_3_2_debit_insufficient_funds(self):
        """TC-3.2: Debit Account with Amount Greater Than Balance"""
        input_text = "3\n2000.00\n4\n"
        output = run_python_program(input_text)
        verify(output, reporter=PythonNativeReporter())
    
    def test_tc_3_3_debit_zero_amount(self):
        """TC-3.3: Debit Account with Zero Amount"""
        input_text = "3\n0.00\n4\n"
        output = run_python_program(input_text)
        verify(output, reporter=PythonNativeReporter())
    
    def test_tc_4_1_exit_application(self):
        """TC-4.1: Exit the Application"""
        input_text = "4\n"
        output = run_python_program(input_text)
        verify(output, reporter=PythonNativeReporter())


class TestBulkComparison(unittest.TestCase):
    """Test en lot pour comparer tous les fichiers approved vs received."""
    
    def test_all_cases_match_approved(self):
        """Compare tous les cas de test avec leurs fichiers approved."""
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
            
            # Lire le fichier approved correspondant
            approved_path = os.path.join(APPROVED_DIR, f"{case_id}.approved.txt")
            if not os.path.exists(approved_path):
                results.append(f"⚠️  {case_id}: Fichier approved manquant")
                continue
            
            with open(approved_path, "r", encoding="utf-8") as f:
                approved_output = f.read()
            
            # Comparer les sorties
            if received_output == approved_output:
                results.append(f"✅ {case_id}: OK")
            else:
                results.append(f"❌ {case_id}: Différence détectée")
                
                # Sauvegarder le fichier received pour debug
                received_path = os.path.join(RECEIVED_DIR, f"{case_id}.received.txt")
                with open(received_path, "w", encoding="utf-8") as f:
                    f.write(received_output)
        
        # Afficher les résultats
        print("\n" + "="*50)
        print("RÉSULTATS DES TESTS D'APPROBATION")
        print("="*50)
        for result in results:
            print(result)
        print("="*50)
        
        # Vérifier qu'aucun cas n'a échoué
        failed_cases = [r for r in results if r.startswith("❌")]
        if failed_cases:
            self.fail(f"{len(failed_cases)} cas de test ont échoué:\n" + "\n".join(failed_cases))


if __name__ == "__main__":
    # Générer les fichiers received avant de lancer les tests
    print("🔄 Génération des fichiers received...")
    from generate_received_files import main as generate_received
    generate_received()
    
    print("\n🧪 Lancement des tests d'approbation...")
    unittest.main(verbosity=2)
