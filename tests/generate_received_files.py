import os
import subprocess
import sys
from typing import Dict, List


# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "inputs")
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


def ensure_dirs() -> None:
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(RECEIVED_DIR, exist_ok=True)


def get_test_cases_from_inputs() -> List[Dict[str, str]]:
    """Lit les fichiers d'entrée existants pour générer les cas de test."""
    cases = []
    
    # Lister tous les fichiers .in dans le répertoire inputs
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


def main() -> None:
    ensure_dirs()

    cases = get_test_cases_from_inputs()
    
    if not cases:
        print("❌ Aucun fichier d'entrée trouvé dans tests/inputs/")
        return
    
    print(f"📋 Trouvé {len(cases)} cas de test")
    
    for case in cases:
        case_id = case["id"]
        input_text = case["input"]

        try:
            output = run_python_program(input_text)
        except Exception as exc:
            print(f"❌ Échec {case_id} : {exc}")
            continue

        received_path = os.path.join(RECEIVED_DIR, f"{case_id}.received.txt")
        with open(received_path, "w", encoding="utf-8") as f_out:
            f_out.write(output)

        print(f"✅ Généré : {received_path}")


if __name__ == "__main__":
    main()
