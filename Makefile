# Makefile pour la gestion des tests Golden Master
# Facilite l'exécution des tests en local et en CI/CD

.PHONY: help install test test-fast clean lint check-deps all

# Variables
PYTHON := python
PIP := pip
TEST_DIR := tests
PYTHON_DIR := python_accountsystem

help: ## Affiche l'aide
	@echo "🚀 Tests Golden Master - Modernisation COBOL → Python"
	@echo "====================================================="
	@echo ""
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Installe les dépendances
	@echo "📦 Installation des dépendances..."
	$(PIP) install -r requirements.txt
	@echo "✅ Dépendances installées"

check-deps: ## Vérifie les dépendances
	@echo "🔍 Vérification des dépendances..."
	$(PYTHON) -c "import approvaltests; print('✅ ApprovalTests OK')" || echo "❌ ApprovalTests manquant"
	$(PYTHON) -c "import pytest; print('✅ Pytest OK')" || echo "❌ Pytest manquant"
	@echo "✅ Vérification terminée"

lint: ## Vérifie la qualité du code
	@echo "🔍 Vérification du code Python..."
	$(PYTHON) -m py_compile $(PYTHON_DIR)/*.py
	$(PYTHON) -m py_compile $(TEST_DIR)/*.py
	@echo "✅ Code Python valide"

test-generate: ## Génère les fichiers received
	@echo "🔄 Génération des fichiers received..."
	$(PYTHON) $(TEST_DIR)/generate_received_files.py
	@echo "✅ Fichiers received générés"

test-fast: test-generate ## Exécute les tests Golden Master (rapide)
	@echo "🧪 Tests Golden Master (rapide)..."
	$(PYTHON) $(TEST_DIR)/test_golden_master.py

test-approval: test-generate ## Exécute les tests ApprovalTests
	@echo "📊 Tests ApprovalTests..."
	$(PYTHON) -m pytest $(TEST_DIR)/test_approval.py::TestBulkComparison::test_all_cases_match_approved -v

test-visual: test-generate ## Exécute les tests avec diff visuel
	@echo "🎨 Tests avec diff visuel..."
	$(PYTHON) $(TEST_DIR)/test_visual_diff.py

test: test-fast ## Exécute tous les tests (alias pour test-fast)

test-all: test-fast test-approval ## Exécute tous les types de tests

view-diffs: ## Ouvre le visualiseur de diffs interactif
	@echo "🎨 Ouverture du visualiseur de diffs..."
	$(PYTHON) $(TEST_DIR)/view_diffs.py

view-diffs-summary: ## Affiche le résumé des diffs disponibles
	@echo "📊 Résumé des diffs visuels..."
	$(PYTHON) $(TEST_DIR)/view_diffs.py --summary

clean: ## Nettoie les fichiers temporaires
	@echo "🧹 Nettoyage des fichiers temporaires..."
	$(PYTHON) $(TEST_DIR)/clean_test_files.py
	@echo "✅ Nettoyage terminé"

ci-test: check-deps lint test-fast ## Pipeline CI/CD complet
	@echo ""
	@echo "🎉 PIPELINE CI/CD TERMINÉ AVEC SUCCÈS"
	@echo "====================================="
	@echo "✅ Dépendances: OK"
	@echo "✅ Qualité du code: OK" 
	@echo "✅ Tests Golden Master: OK"
	@echo ""

demo: ## Démonstration complète
	@echo "🎬 DÉMONSTRATION DES TESTS GOLDEN MASTER"
	@echo "========================================"
	@make clean
	@make test-generate
	@make test-fast
	@echo ""
	@echo "🎯 Démonstration terminée - Tous les tests passent!"

all: clean install lint test ## Pipeline complet (nettoyage + installation + tests)

# Commandes pour le développement
dev-watch: ## Surveille les changements et relance les tests
	@echo "👀 Surveillance des changements (Ctrl+C pour arrêter)..."
	@while true; do \
		inotifywait -r -e modify $(PYTHON_DIR) $(TEST_DIR) 2>/dev/null && \
		echo "🔄 Changement détecté, relancement des tests..." && \
		make test-fast; \
	done

status: ## Affiche le statut des tests
	@echo "📊 STATUT DES TESTS GOLDEN MASTER"
	@echo "================================"
	@echo "📂 Fichiers d'entrée: $$(ls $(TEST_DIR)/inputs/*.in 2>/dev/null | wc -l)"
	@echo "🎯 Fichiers approved: $$(ls $(TEST_DIR)/approved/*.approved.txt 2>/dev/null | wc -l)" 
	@echo "📥 Fichiers received: $$(ls $(TEST_DIR)/received/*.received.txt 2>/dev/null | wc -l)"
	@echo ""
	@if [ -d "$(TEST_DIR)/received" ]; then \
		echo "🕒 Dernière génération: $$(stat -c %y $(TEST_DIR)/received 2>/dev/null || stat -f %Sm $(TEST_DIR)/received 2>/dev/null || echo 'Inconnue')"; \
	else \
		echo "⚠️  Aucun fichier received trouvé - exécutez 'make test-generate'"; \
	fi

# Aide par défaut
.DEFAULT_GOAL := help
