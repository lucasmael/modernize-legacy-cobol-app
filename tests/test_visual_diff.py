#!/usr/bin/env python3
"""
Tests avec diff visuel pour ApprovalTests et Golden Master
Intègre des outils de comparaison visuels pour faciliter le debugging
"""

import os
import subprocess
import sys
import unittest
import difflib
import json
from typing import Dict, List, Optional
from pathlib import Path

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "inputs")
APPROVED_DIR = os.path.join(PROJECT_ROOT, "tests", "approved")
RECEIVED_DIR = os.path.join(PROJECT_ROOT, "tests", "received")
DIFF_DIR = os.path.join(PROJECT_ROOT, "tests", "visual_diffs")
PYTHON_MAIN = os.path.join(PROJECT_ROOT, "python_accountsystem", "main.py")

try:
    from approvaltests import verify
    from approvaltests.reporters import GenericDiffReporter, DiffReporter
    APPROVALTESTS_AVAILABLE = True
except ImportError:
    APPROVALTESTS_AVAILABLE = False


class VisualDiffReporter:
    """Reporter personnalisé avec génération de diffs visuels."""
    
    def __init__(self):
        self.diff_dir = Path(DIFF_DIR)
        self.diff_dir.mkdir(exist_ok=True)
    
    def report(self, received_path: str, approved_path: str) -> None:
        """Génère un rapport visuel des différences."""
        test_name = Path(received_path).stem.replace('.received', '')
        
        try:
            with open(approved_path, 'r', encoding='utf-8') as f:
                approved_content = f.readlines()
        except FileNotFoundError:
            approved_content = ["[FICHIER APPROVED MANQUANT]\n"]
        
        try:
            with open(received_path, 'r', encoding='utf-8') as f:
                received_content = f.readlines()
        except FileNotFoundError:
            received_content = ["[FICHIER RECEIVED MANQUANT]\n"]
        
        # Générer diff HTML
        self._generate_html_diff(test_name, approved_content, received_content)
        
        # Générer diff texte coloré
        self._generate_text_diff(test_name, approved_content, received_content)
        
        # Générer résumé JSON
        self._generate_json_summary(test_name, approved_path, received_path)
    
    def _generate_html_diff(self, test_name: str, approved: List[str], received: List[str]) -> None:
        """Génère un diff HTML avec coloration."""
        differ = difflib.HtmlDiff(wrapcolumn=80)
        html_diff = differ.make_file(
            approved, received,
            fromdesc=f"APPROVED ({test_name})",
            todesc=f"RECEIVED ({test_name})",
            context=True,
            numlines=3
        )
        
        html_path = self.diff_dir / f"{test_name}.diff.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_diff)
        
        print(f"🎨 Diff HTML généré : {html_path}")
    
    def _generate_text_diff(self, test_name: str, approved: List[str], received: List[str]) -> None:
        """Génère un diff texte avec marqueurs visuels."""
        diff_lines = list(difflib.unified_diff(
            approved, received,
            fromfile=f"approved/{test_name}",
            tofile=f"received/{test_name}",
            lineterm='',
            n=3
        ))
        
        if diff_lines:
            diff_path = self.diff_dir / f"{test_name}.diff.txt"
            with open(diff_path, 'w', encoding='utf-8') as f:
                # En-tête avec style
                f.write("=" * 70 + "\n")
                f.write(f"DIFF VISUEL POUR {test_name}\n")
                f.write("=" * 70 + "\n\n")
                
                # Légende
                f.write("LÉGENDE:\n")
                f.write("  - (rouge)  : Ligne supprimée dans APPROVED\n")
                f.write("  + (vert)   : Ligne ajoutée dans RECEIVED\n")
                f.write("  @ (bleu)   : Contexte de position\n\n")
                
                # Diff coloré pour terminal
                for line in diff_lines:
                    if line.startswith('+++') or line.startswith('---'):
                        f.write(f"📁 {line}\n")
                    elif line.startswith('@@'):
                        f.write(f"📍 {line}\n")
                    elif line.startswith('-'):
                        f.write(f"❌ {line}\n")
                    elif line.startswith('+'):
                        f.write(f"✅ {line}\n")
                    else:
                        f.write(f"   {line}\n")
            
            print(f"📝 Diff texte généré : {diff_path}")
    
    def _generate_json_summary(self, test_name: str, approved_path: str, received_path: str) -> None:
        """Génère un résumé JSON des différences."""
        summary = {
            "test_name": test_name,
            "timestamp": subprocess.check_output(['date', '-Iseconds']).decode().strip(),
            "approved_file": approved_path,
            "received_file": received_path,
            "approved_exists": os.path.exists(approved_path),
            "received_exists": os.path.exists(received_path),
            "files_identical": False,
            "line_differences": []
        }
        
        if os.path.exists(approved_path) and os.path.exists(received_path):
            with open(approved_path, 'r') as f:
                approved_lines = f.readlines()
            with open(received_path, 'r') as f:
                received_lines = f.readlines()
            
            summary["files_identical"] = approved_lines == received_lines
            
            # Détailler les différences ligne par ligne
            for i, (approved_line, received_line) in enumerate(zip(approved_lines, received_lines)):
                if approved_line != received_line:
                    summary["line_differences"].append({
                        "line_number": i + 1,
                        "approved": approved_line.strip(),
                        "received": received_line.strip()
                    })
        
        json_path = self.diff_dir / f"{test_name}.summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Résumé JSON généré : {json_path}")


def run_python_program(input_text: str) -> str:
    """Exécute le programme Python avec l'entrée fournie."""
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
            case_id = filename[:-3]
            input_path = os.path.join(INPUT_DIR, filename)
            
            with open(input_path, "r", encoding="utf-8") as f:
                input_text = f.read()
            
            cases.append({
                "id": case_id,
                "input": input_text
            })
    
    return sorted(cases, key=lambda x: x["id"])


class TestVisualDiff(unittest.TestCase):
    """Tests avec diff visuel intégré."""
    
    @classmethod
    def setUpClass(cls):
        """Configuration initiale."""
        os.makedirs(RECEIVED_DIR, exist_ok=True)
        os.makedirs(DIFF_DIR, exist_ok=True)
        cls.visual_diff = VisualDiffReporter()
    
    def test_all_cases_with_visual_diff(self):
        """Teste tous les cas avec génération de diffs visuels."""
        cases = get_test_cases_from_inputs()
        
        if not cases:
            self.skipTest("Aucun cas de test trouvé")
        
        print(f"\n🎨 TESTS AVEC DIFF VISUEL - {len(cases)} cas")
        print("=" * 50)
        
        results = []
        
        for case in cases:
            case_id = case["id"]
            input_text = case["input"]
            
            print(f"\n🧪 Test {case_id}...")
            
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
            
            # Lire le fichier approved
            approved_path = os.path.join(APPROVED_DIR, f"{case_id}.approved.txt")
            if not os.path.exists(approved_path):
                results.append(f"⚠️  {case_id}: Fichier approved manquant")
                continue
            
            with open(approved_path, "r", encoding="utf-8") as f:
                approved_output = f.read()
            
            # Comparer et générer diffs visuels si nécessaire
            if received_output == approved_output:
                results.append(f"✅ {case_id}: CORRESPONDANCE PARFAITE")
                print(f"   ✅ Correspondance parfaite")
            else:
                results.append(f"❌ {case_id}: DIFFÉRENCE DÉTECTÉE")
                print(f"   ❌ Différence détectée - Génération diff visuel...")
                
                # Générer le diff visuel
                self.visual_diff.report(received_path, approved_path)
        
        # Rapport final
        print("\n" + "=" * 60)
        print("RÉSULTATS AVEC DIFF VISUEL")
        print("=" * 60)
        for result in results:
            print(result)
        
        # Statistiques
        success_count = len([r for r in results if r.startswith("✅")])
        total_count = len(results)
        
        print(f"\n📊 Résumé: {success_count}/{total_count} tests réussis")
        
        if success_count < total_count:
            print(f"\n🎨 Diffs visuels disponibles dans: {DIFF_DIR}")
            print("   📁 *.diff.html  - Diff HTML coloré")
            print("   📝 *.diff.txt   - Diff texte avec marqueurs")
            print("   📊 *.summary.json - Résumé structuré")
        
        # Vérifier qu'aucun cas n'a échoué
        failed_cases = [r for r in results if r.startswith("❌")]
        if failed_cases:
            self.fail(f"{len(failed_cases)} cas de test ont échoué:\n" + "\n".join(failed_cases))


class TestApprovalTestsWithVisualDiff(unittest.TestCase):
    """Tests ApprovalTests avec reporter visuel personnalisé."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        os.makedirs(RECEIVED_DIR, exist_ok=True)
        if not APPROVALTESTS_AVAILABLE:
            self.skipTest("ApprovalTests non disponible")
    
    def test_tc_1_1_with_visual_diff(self):
        """TC-1.1 avec diff visuel."""
        input_text = "1\n4\n"
        output = run_python_program(input_text)
        
        # Utiliser un reporter personnalisé qui génère des diffs visuels
        visual_reporter = VisualDiffReporter()
        
        try:
            verify(output, reporter=GenericDiffReporter(['echo', 'Diff détecté']))
        except Exception as e:
            # En cas d'échec, générer le diff visuel
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.received.txt', delete=False) as f:
                f.write(output)
                received_path = f.name
            
            approved_path = received_path.replace('.received.txt', '.approved.txt')
            visual_reporter.report(received_path, approved_path)
            raise


def main():
    """Point d'entrée principal."""
    print("🎨 TESTS AVEC DIFF VISUEL")
    print("=" * 40)
    
    if not APPROVALTESTS_AVAILABLE:
        print("⚠️  ApprovalTests non disponible - Tests de base uniquement")
    
    # Créer les répertoires nécessaires
    os.makedirs(DIFF_DIR, exist_ok=True)
    
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
