# Makefile per facilitare le operazioni di sviluppo e testing

.PHONY: help test lint coverage clean docker-build docker-run dev

help:
	@echo "Makefile di Compliance Compass"
	@echo ""
	@echo "Utilizzo:"
	@echo "    make test             Esegue tutti i test"
	@echo "    make test-unit        Esegue solo i test unitari"
	@echo "    make test-integration Esegue solo i test di integrazione"
	@echo "    make test-performance Esegue i test di performance"
	@echo "    make test-security    Esegue i test di sicurezza"
	@echo "    make lint             Esegue il linting del codice con flake8"
	@echo "    make format           Formatta il codice con black"
	@echo "    make coverage         Genera il rapporto di copertura dei test"
	@echo "    make clean            Rimuove file temporanei e cache"
	@echo "    make docker-build     Costruisce l'immagine Docker"
	@echo "    make docker-run       Avvia i container Docker"
	@echo "    make dev              Avvia l'ambiente di sviluppo"

test:
	pytest -vxs

test-unit:
	pytest tests/unit -vxs

test-integration:
	pytest tests/integration -vxs

test-performance:
	pytest tests/performance -vxs

test-security:
	pytest tests/security -vxs

lint:
	flake8 src tests

format:
	black src tests

coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage_report

docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000