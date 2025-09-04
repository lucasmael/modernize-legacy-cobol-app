#!/usr/bin/env python3
"""
Script pour nettoyer les fichiers de test générés.

Ce script supprime :
- Les fichiers received
- Les fichiers approval temporaires générés par ApprovalTests
- Les caches Python (__pycache__)
"""

import os
import shutil
import glob


def clean_received_files():
    """Supprime tous les fichiers received."""
    received_dir = os.path.join(os.path.dirname(__file__), "received")
    if os.path.exists(received_dir):
        print(f"🧹 Nettoyage du répertoire: {received_dir}")
        shutil.rmtree(received_dir)
        print("✅ Fichiers received supprimés")
    else:
        print("ℹ️  Aucun fichier received à nettoyer")


def clean_approval_files():
    """Supprime les fichiers temporaires d'ApprovalTests."""
    test_dir = os.path.dirname(__file__)
    
    # Chercher tous les fichiers .approved.txt et .received.txt générés par ApprovalTests
    patterns = [
        "TestPythonAccountSystem.*.approved.txt",
        "TestPythonAccountSystem.*.received.txt",
        "TestGoldenMaster.*.approved.txt",
        "TestGoldenMaster.*.received.txt"
    ]
    
    files_removed = 0
    for pattern in patterns:
        files = glob.glob(os.path.join(test_dir, pattern))
        for file_path in files:
            os.remove(file_path)
            files_removed += 1
            print(f"🗑️  Supprimé: {os.path.basename(file_path)}")
    
    if files_removed > 0:
        print(f"✅ {files_removed} fichiers ApprovalTests supprimés")
    else:
        print("ℹ️  Aucun fichier ApprovalTests à nettoyer")


def clean_python_cache():
    """Supprime les caches Python."""
    test_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(test_dir)
    
    cache_dirs = [
        os.path.join(test_dir, "__pycache__"),
        os.path.join(project_root, "python_accountsystem", "__pycache__"),
        os.path.join(project_root, "__pycache__")
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"🧹 Cache supprimé: {cache_dir}")
    
    print("✅ Caches Python nettoyés")


def clean_pytest_cache():
    """Supprime le cache pytest."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    pytest_cache = os.path.join(project_root, ".pytest_cache")
    
    if os.path.exists(pytest_cache):
        shutil.rmtree(pytest_cache)
        print("🧹 Cache pytest supprimé")
    else:
        print("ℹ️  Aucun cache pytest à nettoyer")


def main():
    """Point d'entrée principal."""
    print("🧹 Nettoyage des fichiers de test")
    print("="*40)
    
    clean_received_files()
    clean_approval_files() 
    clean_python_cache()
    clean_pytest_cache()
    
    print("="*40)
    print("🎉 Nettoyage terminé!")


if __name__ == "__main__":
    main()
