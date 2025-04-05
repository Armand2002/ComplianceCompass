#!/bin/bash

# Script per eseguire test di Compliance Compass

# Colori per output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Funzione per stampare messaggi
print_message() {
    echo -e "${1}${2}${NC}"
}

# Controllo prerequisiti
check_prerequisites() {
    # Verifica installazione dipendenze
    if ! command -v pytest &> /dev/null; then
        print_message "${RED}" "Errore: pytest non installato"
        print_message "${RED}" "Installare con: pip install pytest pytest-cov"
        exit 1
    fi
}

# Esegui test
run_tests() {
    print_message "${GREEN}" "🚀 Avvio test di Compliance Compass 🚀"
    
    # Opzioni per l'esecuzione dei test
    local test_options=(
        "-v"                    # Verbose
        "--cov=src"             # Copertura codice
        "--cov-report=term"     # Report copertura in terminale
        "--cov-report=html"     # Report HTML dettagliato
        "tests/"                # Directory dei test
    )
    
    # Flag per test specifici (opzionale)
    local test_filter="${1:-}"
    if [[ -n "$test_filter" ]]; then
        test_options+=("-k" "$test_filter")
    fi
    
    # Esecuzione
    python -m pytest "${test_options[@]}"
    
    # Cattura lo stato di uscita
    local exit_code=$?
    
    # Stampa risultato
    if [[ $exit_code -eq 0 ]]; then
        print_message "${GREEN}" "✅ Test completati con successo!"
    else
        print_message "${RED}" "❌ Alcuni test sono falliti"
    fi
    
    return $exit_code
}

# Funzione principale
main() {
    check_prerequisites
    run_tests "$@"
}

# Esegui lo script
main "$@"