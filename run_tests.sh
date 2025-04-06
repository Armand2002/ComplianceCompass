#!/bin/bash
# run_tests.sh - Script completo per eseguire tutti i tipi di test

set -e  # Exit on first error

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funzione per stampare header
print_header() {
    echo -e "\n${BLUE}====== $1 ======${NC}\n"
}

# Funzione per stampare risultato
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2 completato con successo${NC}"
    else
        echo -e "${RED}✗ $2 fallito${NC}"
        exit $1
    fi
}

# Verifica ambiente
print_header "Verifica ambiente"
python -m pip install -r requirements.txt
python -m pip install -r requirements-test.txt
python -c "import pytest, coverage" || (echo "Installazioni mancanti" && exit 1)
print_result $? "Verifica ambiente"

# Linting
print_header "Linting con flake8"
python -m flake8 src tests
print_result $? "Linting"

# Controllo sicurezza
print_header "Analisi di sicurezza con bandit"
python -m bandit -r src
print_result $? "Analisi sicurezza"

# Test unitari
print_header "Esecuzione test unitari"
python -m pytest tests/unit/ --cov=src --cov-report=term --cov-report=xml --cov-report=html
UNIT_RESULT=$?
COV_PERCENT=$(python -c "import xml.etree.ElementTree as ET; tree = ET.parse('coverage.xml'); root = tree.getroot(); print(root.attrib['line-rate'])")
COV_PERCENT=$(echo "$COV_PERCENT * 100" | bc)
echo -e "Copertura del codice: ${YELLOW}${COV_PERCENT}%${NC}"
print_result $UNIT_RESULT "Test unitari"

# Test di integrazione
print_header "Esecuzione test di integrazione"
python -m pytest tests/integration/
print_result $? "Test di integrazione"

# Test E2E (opzionale)
if [ "$1" == "--full" ]; then
    print_header "Esecuzione test end-to-end"
    python -m pytest tests/e2e/
    print_result $? "Test end-to-end"
fi

# Test di performance (opzionale)
if [ "$1" == "--full" ] || [ "$1" == "--perf" ]; then
    print_header "Esecuzione test di performance"
    python -m pytest tests/performance/ --run-performance
    print_result $? "Test di performance"
fi

# Report finale
print_header "Report finale"
echo -e "${GREEN}Tutti i test sono stati eseguiti con successo!${NC}"
echo -e "Report di copertura dettagliato: ${YELLOW}htmlcov/index.html${NC}"

exit 0