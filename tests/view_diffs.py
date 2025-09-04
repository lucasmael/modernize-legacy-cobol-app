#!/usr/bin/env python3
"""
Visualiseur de diffs pour les tests Golden Master
Ouvre automatiquement les diffs HTML dans le navigateur
"""

import os
import sys
import webbrowser
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


def get_available_diffs(diff_dir: Path) -> List[Dict[str, str]]:
    """Récupère la liste des diffs disponibles."""
    diffs = []
    
    if not diff_dir.exists():
        return diffs
    
    for html_file in diff_dir.glob("*.diff.html"):
        test_name = html_file.stem.replace('.diff', '')
        
        diff_info = {
            "test_name": test_name,
            "html_file": str(html_file),
            "txt_file": str(diff_dir / f"{test_name}.diff.txt"),
            "json_file": str(diff_dir / f"{test_name}.summary.json")
        }
        
        # Ajouter les métadonnées du JSON si disponible
        json_path = diff_dir / f"{test_name}.summary.json"
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
                diff_info.update(summary)
            except Exception:
                pass
        
        diffs.append(diff_info)
    
    return sorted(diffs, key=lambda x: x["test_name"])


def print_diff_summary(diffs: List[Dict[str, str]]) -> None:
    """Affiche un résumé des diffs disponibles."""
    if not diffs:
        print("ℹ️  Aucun diff visuel disponible")
        return
    
    print(f"🎨 {len(diffs)} diff(s) visuel(s) disponible(s):")
    print("-" * 50)
    
    for i, diff in enumerate(diffs, 1):
        test_name = diff["test_name"]
        identical = diff.get("files_identical", False)
        status = "✅ Identique" if identical else "❌ Différent"
        
        print(f"{i:2d}. {test_name} - {status}")
        
        if "line_differences" in diff:
            line_count = len(diff["line_differences"])
            if line_count > 0:
                print(f"     └─ {line_count} ligne(s) différente(s)")


def open_diff_in_browser(diff_info: Dict[str, str]) -> None:
    """Ouvre le diff HTML dans le navigateur."""
    html_file = diff_info["html_file"]
    
    if not os.path.exists(html_file):
        print(f"❌ Fichier HTML introuvable: {html_file}")
        return
    
    try:
        # Convertir en URL file://
        file_url = Path(html_file).as_uri()
        webbrowser.open(file_url)
        print(f"🌐 Ouverture dans le navigateur: {diff_info['test_name']}")
    except Exception as e:
        print(f"❌ Erreur ouverture navigateur: {e}")
        print(f"📁 Fichier disponible: {html_file}")


def show_text_diff(diff_info: Dict[str, str]) -> None:
    """Affiche le diff texte dans le terminal."""
    txt_file = diff_info["txt_file"]
    
    if not os.path.exists(txt_file):
        print(f"❌ Fichier texte introuvable: {txt_file}")
        return
    
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Utiliser un pager si disponible
        if sys.stdout.isatty():
            try:
                subprocess.run(['less', '-R'], input=content, text=True)
                return
            except FileNotFoundError:
                pass
        
        print(content)
    except Exception as e:
        print(f"❌ Erreur lecture fichier: {e}")


def open_diff_tool(diff_info: Dict[str, str]) -> None:
    """Ouvre un outil de diff externe (VSCode, Meld, etc.)."""
    test_name = diff_info["test_name"]
    
    # Chemins des fichiers à comparer
    project_root = Path(__file__).parent.parent
    approved_file = project_root / "tests" / "approved" / f"{test_name}.approved.txt"
    received_file = project_root / "tests" / "received" / f"{test_name}.received.txt"
    
    if not approved_file.exists() or not received_file.exists():
        print("❌ Fichiers approved/received introuvables")
        return
    
    # Essayer différents outils de diff
    diff_tools = [
        ['code', '--diff', str(approved_file), str(received_file)],  # VSCode
        ['meld', str(approved_file), str(received_file)],             # Meld
        ['kdiff3', str(approved_file), str(received_file)],           # KDiff3
        ['vimdiff', str(approved_file), str(received_file)],          # Vim
    ]
    
    for tool_cmd in diff_tools:
        try:
            subprocess.run(tool_cmd, check=True)
            print(f"🔧 Ouvert avec {tool_cmd[0]}")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    print("❌ Aucun outil de diff externe trouvé")
    print("💡 Installez VSCode, Meld, KDiff3 ou Vim pour la comparaison externe")


def interactive_mode(diffs: List[Dict[str, str]]) -> None:
    """Mode interactif pour naviguer dans les diffs."""
    while True:
        print("\n" + "=" * 50)
        print("🎨 VISUALISEUR DE DIFFS - MODE INTERACTIF")
        print("=" * 50)
        
        print_diff_summary(diffs)
        
        if not diffs:
            return
        
        print("\nCommandes disponibles:")
        print("  [numéro]  - Ouvrir diff HTML dans navigateur")
        print("  t[numéro] - Afficher diff texte dans terminal")
        print("  d[numéro] - Ouvrir avec outil de diff externe")
        print("  r         - Rafraîchir la liste")
        print("  q         - Quitter")
        
        try:
            choice = input("\nVotre choix: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'r':
                # Rafraîchir la liste
                diff_dir = Path(__file__).parent / "visual_diffs"
                diffs = get_available_diffs(diff_dir)
                continue
            elif choice.startswith('t') and len(choice) > 1:
                # Afficher diff texte
                try:
                    index = int(choice[1:]) - 1
                    if 0 <= index < len(diffs):
                        show_text_diff(diffs[index])
                    else:
                        print("❌ Numéro invalide")
                except ValueError:
                    print("❌ Format invalide (ex: t1)")
            elif choice.startswith('d') and len(choice) > 1:
                # Ouvrir outil externe
                try:
                    index = int(choice[1:]) - 1
                    if 0 <= index < len(diffs):
                        open_diff_tool(diffs[index])
                    else:
                        print("❌ Numéro invalide")
                except ValueError:
                    print("❌ Format invalide (ex: d1)")
            elif choice.isdigit():
                # Ouvrir HTML dans navigateur
                index = int(choice) - 1
                if 0 <= index < len(diffs):
                    open_diff_in_browser(diffs[index])
                else:
                    print("❌ Numéro invalide")
            else:
                print("❌ Commande non reconnue")
        
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except EOFError:
            break


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualiseur de diffs pour tests Golden Master")
    parser.add_argument('--all', action='store_true', help="Ouvrir tous les diffs HTML")
    parser.add_argument('--test', type=str, help="Ouvrir le diff d'un test spécifique")
    parser.add_argument('--text', action='store_true', help="Afficher en mode texte")
    parser.add_argument('--tool', action='store_true', help="Ouvrir avec outil externe")
    parser.add_argument('--summary', action='store_true', help="Afficher uniquement le résumé")
    
    args = parser.parse_args()
    
    # Trouver le répertoire des diffs
    diff_dir = Path(__file__).parent / "visual_diffs"
    diffs = get_available_diffs(diff_dir)
    
    if args.summary:
        print_diff_summary(diffs)
        return
    
    if not diffs:
        print("ℹ️  Aucun diff visuel disponible")
        print("💡 Exécutez d'abord: python tests/test_visual_diff.py")
        return
    
    if args.all:
        # Ouvrir tous les diffs HTML
        for diff in diffs:
            open_diff_in_browser(diff)
    elif args.test:
        # Ouvrir un test spécifique
        target_diff = next((d for d in diffs if d["test_name"] == args.test), None)
        if target_diff:
            if args.text:
                show_text_diff(target_diff)
            elif args.tool:
                open_diff_tool(target_diff)
            else:
                open_diff_in_browser(target_diff)
        else:
            print(f"❌ Test '{args.test}' introuvable")
            print_diff_summary(diffs)
    else:
        # Mode interactif
        interactive_mode(diffs)


if __name__ == "__main__":
    main()
