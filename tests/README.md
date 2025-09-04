# Tests Golden Master pour la Modernisation COBOL → Python

Ce répertoire contient les tests Golden Master pour vérifier que le programme Python reproduit fidèlement le comportement du programme COBOL original.

## Structure des Tests

```
tests/
├── inputs/           # Fichiers d'entrée pour les cas de test
├── approved/         # Sorties "golden master" du programme COBOL
├── received/         # Sorties générées par le programme Python
├── generate_golden_masters.py    # Script pour générer les approved (COBOL)
├── generate_received_files.py    # Script pour générer les received (Python)
├── test_golden_master.py         # Tests Golden Master principaux
├── test_approval.py              # Tests utilisant ApprovalTests
└── README.md                     # Ce fichier
```

## Cas de Test

| ID     | Description                                        | Fichier d'entrée |
|--------|----------------------------------------------------|------------------|
| TC-1.1 | Afficher le solde actuel                          | TC-1.1.in        |
| TC-2.1 | Créditer le compte avec un montant valide         | TC-2.1.in        |
| TC-2.2 | Créditer le compte avec un montant zéro           | TC-2.2.in        |
| TC-3.1 | Débiter le compte avec un montant valide          | TC-3.1.in        |
| TC-3.2 | Débiter le compte avec un montant supérieur au solde | TC-3.2.in      |
| TC-3.3 | Débiter le compte avec un montant zéro            | TC-3.3.in        |
| TC-4.1 | Quitter l'application                              | TC-4.1.in        |

## Comment Utiliser les Tests

### 1. Génération des Fichiers Golden Master (approved)

Les fichiers approved sont générés à partir du programme COBOL original :

```bash
python tests/generate_golden_masters.py
```

Cette commande :
- Exécute le binaire COBOL (`./accountsystem`) avec chaque cas de test
- Sauvegarde les sorties dans `tests/approved/`

### 2. Génération des Fichiers Received (Python)

Les fichiers received sont générés à partir du programme Python :

```bash
python tests/generate_received_files.py
```

Cette commande :
- Exécute le programme Python (`python_accountsystem/main.py`) avec chaque cas de test
- Sauvegarde les sorties dans `tests/received/`

### 3. Exécution des Tests Golden Master

#### Option A : Tests Golden Master Simples

```bash
python tests/test_golden_master.py
```

Cette méthode :
- Compare directement les fichiers approved vs received
- Affiche un rapport détaillé des résultats
- **Recommandée** pour la plupart des utilisations

#### Option B : Tests avec ApprovalTests

```bash
# Installer les dépendances
pip install -r requirements.txt

# Exécuter les tests avec pytest
pytest tests/test_approval.py -v

# Ou directement avec Python
python tests/test_approval.py
```

Cette méthode utilise la bibliothèque ApprovalTests pour :
- Comparer les sorties avec des outils de diff visuels
- Faciliter l'approbation de nouvelles sorties

### 4. Script Tout-en-Un

Pour une exécution complète automatisée :

```bash
python run_tests.py
```

Ce script :
1. Vérifie les prérequis
2. Génère les fichiers received
3. Lance les tests d'approbation
4. Affiche un rapport complet

## Interprétation des Résultats

### ✅ Tests Réussis
```
✅ TC-1.1: CORRESPONDANCE PARFAITE
✅ TC-2.1: CORRESPONDANCE PARFAITE
...
🎉 TOUS LES TESTS GOLDEN MASTER ONT RÉUSSI!
```

Cela signifie que le programme Python produit exactement la même sortie que le programme COBOL.

### ❌ Tests Échoués
```
❌ TC-2.1: DIFFÉRENCE DÉTECTÉE
```

En cas d'échec, le test affichera :
- Les différences ligne par ligne
- Les fichiers received et approved pour comparaison manuelle

## Maintenir les Tests

### Ajouter de Nouveaux Cas de Test

1. Créer un nouveau fichier dans `tests/inputs/` (ex: `TC-5.1.in`)
2. Ajouter le contenu d'entrée simulé
3. Régénérer les fichiers approved et received
4. Les tests détecteront automatiquement le nouveau cas

### Modifier les Tests Existants

1. Modifier le fichier d'entrée correspondant
2. Régénérer les fichiers approved avec COBOL
3. Régénérer les fichiers received avec Python
4. Relancer les tests

### Dépannage

**Problème** : Tests échouent après modification du code Python
- **Solution** : Régénérer les fichiers received et vérifier les différences

**Problème** : Erreur "Programme Python introuvable"
- **Solution** : Vérifier que `python_accountsystem/main.py` existe

**Problème** : Erreur "Fichiers approved manquants"
- **Solution** : Exécuter `generate_golden_masters.py` d'abord

## Architecture des Tests

Les tests suivent le pattern **Golden Master Testing** :

1. **Golden Master** : Sortie de référence du système legacy (COBOL)
2. **Système Testé** : Nouvelle implémentation (Python)
3. **Comparaison** : Vérification que les sorties sont identiques

Cette approche est idéale pour :
- Moderniser des systèmes legacy
- Garantir la compatibilité comportementale
- Détecter les régressions pendant la migration

## Outils et Dépendances

- **Python 3.x** : Runtime pour les tests et le programme modernisé
- **ApprovalTests** : Bibliothèque de tests d'approbation (optionnel)
- **pytest** : Framework de test (optionnel, utilisé par ApprovalTests)
- **Subprocess** : Pour exécuter les programmes external

## Conseils d'Utilisation

1. **Toujours régénérer les approved avant les received** lors de modifications COBOL
2. **Utiliser le test en lot** (`test_all_cases_match_golden_master`) pour un aperçu rapide
3. **Examiner les fichiers received** manuellement en cas de différences
4. **Archiver les fichiers received** une fois les tests validés (pour historique)
# Test modification pour déclencher le CI/CD
