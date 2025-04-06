# tests/performance/test_performance.py
"""
Test di performance per componenti critici.
"""
import pytest
import time
import statistics
from typing import List, Dict, Any
from unittest.mock import patch
from fastapi.testclient import TestClient

from tests.factories.test_data_factory import TestDataFactory
from src.services.search_service import SearchService

@pytest.mark.performance
class TestPerformance:
    """Test di performance per componenti critici."""
    
    @pytest.fixture
    def performance_config(self):
        """Configurazione per test di performance."""
        return {
            "iterations": 10,
            "thresholds": {
                "search_simple": 0.1,  # 100ms
                "search_complex": 0.3,  # 300ms
                "pattern_create": 0.2,  # 200ms
                "pattern_retrieve": 0.05  # 50ms
            }
        }
    
    def measure_execution_time(self, func, *args, **kwargs):
        """
        Misura il tempo di esecuzione di una funzione.
        
        Args:
            func: Funzione da misurare
            *args, **kwargs: Argomenti da passare alla funzione
            
        Returns:
            tuple: (result, execution_time)
        """
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    
    def test_search_performance(self, client, user_token, performance_config, test_metrics):
        """Verifica la performance della ricerca."""
        headers = {"Authorization": f"Bearer {user_token}"}
        times = []
        
        # Esegui ricerca semplice più volte
        for _ in range(performance_config["iterations"]):
            query_params = TestDataFactory.create_query_params(search_term="test")
            
            _, duration = self.measure_execution_time(
                client.get,
                "/api/search/patterns",
                params=query_params,
                headers=headers
            )
            
            times.append(duration)
        
        # Calcola statistiche
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        
        # Record metrics
        test_metrics.record(
            "search_performance", 
            avg_time, 
            "passed" if avg_time < performance_config["thresholds"]["search_simple"] else "failed"
        )
        
        # Verifica che le performance siano accettabili
        assert avg_time < performance_config["thresholds"]["search_simple"], \
            f"Search should take less than {performance_config['thresholds']['search_simple']}s, took {avg_time}s"
        
        # Log dei risultati
        print(f"Search Performance: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s, p95={p95_time:.4f}s")
    
    def test_pattern_creation_performance(self, client, admin_token, performance_config, test_metrics):
        """Verifica la performance della creazione di pattern."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        times = []
        created_patterns = []
        
        # Crea pattern più volte
        for i in range(performance_config["iterations"]):
            pattern_data = TestDataFactory.create_pattern_data(
                strategy=f"TestStrategy{i}",
                mvc_component="Model",
                complexity="high"
            )
            
            response, duration = self.measure_execution_time(
                client.post,
                "/api/patterns/",
                json=pattern_data,
                headers=headers
            )
            
            times.append(duration)
            
            # Salva ID per cleanup
            if response.status_code == 201:
                created_patterns.append(response.json()["id"])
        
        # Calcola statistiche
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
        
        # Record metrics
        test_metrics.record(
            "pattern_creation_performance", 
            avg_time, 
            "passed" if avg_time < performance_config["thresholds"]["pattern_create"] else "failed"
        )
        
        # Verifica che le performance siano accettabili
        assert avg_time < performance_config["thresholds"]["pattern_create"], \
            f"Pattern creation should take less than {performance_config['thresholds']['pattern_create']}s, took {avg_time}s"
        
        # Log dei risultati
        print(f"Pattern Creation Performance: avg={avg_time:.4f}s, min={min_time:.4f}s, max={max_time:.4f}s, p95={p95_time:.4f}s")
        
        # Cleanup
        for pattern_id in created_patterns:
            client.delete(f"/api/patterns/{pattern_id}", headers=headers)