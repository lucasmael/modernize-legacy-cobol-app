#!/usr/bin/env python3
"""
Script principal pour exécuter les tests d'approbation du système de compte Python.

Ce script :
1. Génère les fichiers received à partir du programme Python
2. Lance les tests d'approbation pour comparer avec les fichiers approved
3. Affiche un rapport détaillé des résultats
"""

import os
import sys
import subprocess


def main():
    """Point d'entrée principal."""
    print("🚀 Lancement des tests d'approbation pour le système de compte Python")
    print("="*70)
    
    # Vérifier que nous sommes dans le bon répertoire
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Vérifier les dépendances
    try:
        import approvaltests
        print("✅ ApprovalTests est installé")
    except ImportError:
        print("❌ ApprovalTests n'est pas installé")
        print("💡 Installez-le avec: pip install -r requirements.txt")
        return 1
    
    # Vérifier que le programme Python existe
    python_main = os.path.join("python_accountsystem", "main.py")
    if not os.path.exists(python_main):
        print(f"❌ Programme Python introuvable: {python_main}")
        return 1
    
    print(f"✅ Programme Python trouvé: {python_main}")
    
    # Vérifier les fichiers d'entrée
    input_dir = os.path.join("tests", "inputs")
    if not os.path.exists(input_dir):
        print(f"❌ Répertoire d'entrée introuvable: {input_dir}")
        return 1
    
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.in')]
    print(f"✅ {len(input_files)} fichiers d'entrée trouvés")
    
    # Vérifier les fichiers approved
    approved_dir = os.path.join("tests", "approved")
    if not os.path.exists(approved_dir):
        print(f"❌ Répertoire approved introuvable: {approved_dir}")
        return 1
    
    approved_files = [f for f in os.listdir(approved_dir) if f.endswith('.approved.txt')]
    print(f"✅ {len(approved_files)} fichiers approved trouvés")
    
    print("\n🔄 Étape 1: Génération des fichiers received...")
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join("tests", "generate_received_files.py")
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Erreur lors de la génération des fichiers received:")
            print(result.stderr)
            return 1
        
        print(result.stdout)
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return 1
    
    print("\n🧪 Étape 2: Lancement des tests d'approbation...")
    try:
        result = subprocess.run([
            sys.executable, 
            "-m", "pytest", 
            os.path.join("tests", "test_approval.py"),
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Erreurs/Avertissements:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n🎉 Tous les tests d'approbation ont réussi!")
            return 0
        else:
            print(f"\n❌ Certains tests ont échoué (code de retour: {result.returncode})")
            return result.returncode
            
    except FileNotFoundError:
        print("❌ pytest n'est pas installé. Essayons avec unittest...")
        try:
            result = subprocess.run([
                sys.executable, 
                os.path.join("tests", "test_approval.py")
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("Erreurs/Avertissements:")
                print(result.stderr)
            
            if result.returncode == 0:
                print("\n🎉 Tous les tests d'approbation ont réussi!")
                return 0
            else:
                print(f"\n❌ Certains tests ont échoué (code de retour: {result.returncode})")
                return result.returncode
        except Exception as e:
            print(f"❌ Erreur lors du lancement des tests: {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
