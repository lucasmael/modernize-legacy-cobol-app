import os
import subprocess
from typing import Dict, List


# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(PROJECT_ROOT, "tests", "inputs")
APPROVED_DIR = os.path.join(PROJECT_ROOT, "tests", "approved")

# Utiliser la variable d'environnement si fournie, sinon défaut sur ./accountsystem
COBOL_EXECUTABLE = os.environ.get("COBOL_EXECUTABLE", os.path.join(PROJECT_ROOT, "accountsystem"))


def run_cobol(input_text: str) -> str:
    """Exécute le binaire COBOL avec l'entrée fournie et renvoie la sortie stdout en texte."""
    result = subprocess.run(
        [COBOL_EXECUTABLE],
        input=input_text.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Erreur d'exécution COBOL: {result.stderr.decode(errors='replace')}")

    return result.stdout.decode(errors="replace")


def ensure_dirs() -> None:
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(APPROVED_DIR, exist_ok=True)


def build_test_cases() -> List[Dict[str, str]]:
    """Construit la liste des cas de test avec leurs entrées simulées."""
    cases = [
        {
            "id": "TC-1.1",
            "desc": "View Current Balance",
            # 1 = View Balance, 4 = Exit
            "input": "1\n4\n",
        },
        {
            "id": "TC-2.1",
            "desc": "Credit Account with Valid Amount",
            # 2 = Credit, 100.00 amount, 4 = Exit
            "input": "2\n100.00\n4\n",
        },
        {
            "id": "TC-2.2",
            "desc": "Credit Account with Zero Amount",
            # 2 = Credit, 0.00 amount, 4 = Exit
            "input": "2\n0.00\n4\n",
        },
        {
            "id": "TC-3.1",
            "desc": "Debit Account with Valid Amount",
            # 3 = Debit, 50.00 amount, 4 = Exit
            "input": "3\n50.00\n4\n",
        },
        {
            "id": "TC-3.2",
            "desc": "Debit Account with Amount Greater Than Balance",
            # 3 = Debit, 2000.00 amount (insufficient), 4 = Exit
            "input": "3\n2000.00\n4\n",
        },
        {
            "id": "TC-3.3",
            "desc": "Debit Account with Zero Amount",
            # 3 = Debit, 0.00 amount, 4 = Exit
            "input": "3\n0.00\n4\n",
        },
        {
            "id": "TC-4.1",
            "desc": "Exit the Application",
            # 4 = Exit
            "input": "4\n",
        },
    ]
    return cases


def main() -> None:
    ensure_dirs()

    cases = build_test_cases()
    for case in cases:
        case_id = case["id"]
        input_text = case["input"]

        # Sauvegarder aussi les inputs pour trace/débogage
        input_path = os.path.join(INPUT_DIR, f"{case_id}.in")
        with open(input_path, "w", encoding="utf-8") as f_in:
            f_in.write(input_text)

        try:
            output = run_cobol(input_text)
        except Exception as exc:
            print(f"❌ Échec {case_id} : {exc}")
            continue

        approved_path = os.path.join(APPROVED_DIR, f"{case_id}.approved.txt")
        with open(approved_path, "w", encoding="utf-8") as f_out:
            f_out.write(output)

        print(f"✅ Généré : {approved_path}")


if __name__ == "__main__":
    main()


