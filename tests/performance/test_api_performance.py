# tests/performance/test_api_performance.py
"""
Test di performance per API endpoints critici.

Misura tempi di risposta e throughput per scenari di uso comune.
Include test concorrenti e profili di carico variabile.
"""
import pytest
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Callable
from pathlib import Path
import logging
from fastapi.testclient import TestClient

logger = logging.getLogger(__name__)

@pytest.mark.performance
class TestAPIPerformance:
    """
    Test di performance per API critiche.
    Richiede flag --run-performance per essere eseguito.
    """
    
    @pytest.fixture(autouse=True)
    def skip_if_not_performance(self, request):
        """Skip se non esplicitamente richiesto."""
        if not request.config.getoption("--run-performance"):
            pytest.skip("Salta test di performance (usa --run-performance)")
    
    @pytest.fixture
    def benchmark_data(self):
        """Prepara dati per il benchmark."""
        return {
            "repetitions": 10,
            "concurrent_users": [1, 5, 10],
            "endpoints": [
                {"url": "/api/patterns/", "method": "get", "expected_status": 200, "max_avg_ms": 200, "max_p95_ms": 300},
                {"url": "/api/search/patterns?q=test", "method": "get", "expected_status": 200, "max_avg_ms": 250, "max_p95_ms": 350},
                {"url": "/api/health/", "method": "get", "expected_status": 200, "max_avg_ms": 50, "max_p95_ms": 100}
            ]
        }
    
    def test_endpoint_response_times(self, client, user_token, benchmark_data):
        """Misura tempo di risposta per endpoint chiave."""
        results = self._run_endpoint_tests(client, user_token, benchmark_data)
        self._validate_and_log_results(results, "endpoint_response")
    
    def test_concurrent_requests(self, client, user_token, benchmark_data):
        """Misura prestazioni con richieste concorrenti."""
        results = self._run_concurrency_tests(client, user_token, benchmark_data)
        self._validate_and_log_results(results, "concurrent_requests")
    
    def test_load_profile(self, client, user_token, benchmark_data):
        """Test con profilo di carico variabile."""
        results = self._run_load_profile_tests(client, user_token, benchmark_data)
        self._validate_and_log_results(results, "load_profile")
    
    def test_pattern_operations_performance(self, client, admin_token, db_session):
        """
        Test completo delle operazioni CRUD sui pattern per misurare performance.
        Misura tempi di creazione, lettura, aggiornamento ed eliminazione.
        """
        headers = {"Authorization": f"Bearer {admin_token}"}
        operation_times = {
            "create": [],
            "read": [],
            "update": [], 
            "delete": []
        }
        
        # Test di creazione
        for i in range(5):
            pattern_data = {
                "title": f"Performance Test Pattern {i}",
                "description": "Pattern for performance testing",
                "context": "Performance testing context",
                "problem": "Need to measure system performance",
                "solution": "Create comprehensive performance tests",
                "consequences": "Better system reliability",
                "strategy": "Test",
                "mvc_component": "Model"
            }
            
            start_time = time.time()
            response = client.post("/api/patterns/", json=pattern_data, headers=headers)
            end_time = time.time()
            
            assert response.status_code == 201, f"Creazione pattern fallita: {response.text}"
            pattern_id = response.json()["id"]
            
            operation_times["create"].append((end_time - start_time) * 1000)
            
            # Test di lettura
            start_time = time.time()
            response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
            end_time = time.time()
            
            assert response.status_code == 200
            operation_times["read"].append((end_time - start_time) * 1000)
            
            # Test di aggiornamento
            update_data = {
                "title": f"Updated Performance Test Pattern {i}",
                "description": "Updated description for performance testing"
            }
            
            start_time = time.time()
            response = client.put(f"/api/patterns/{pattern_id}", json=update_data, headers=headers)
            end_time = time.time()
            
            assert response.status_code == 200
            operation_times["update"].append((end_time - start_time) * 1000)
            
            # Test di eliminazione
            start_time = time.time()
            response = client.delete(f"/api/patterns/{pattern_id}", headers=headers)
            end_time = time.time()
            
            assert response.status_code == 204
            operation_times["delete"].append((end_time - start_time) * 1000)
        
        # Verifica performance
        for operation, times in operation_times.items():
            avg_time = statistics.mean(times)
            p95_time = sorted(times)[int(len(times) * 0.95)] if times else 0
            
            # Soglie di performance specifiche per tipo di operazione
            max_avg = {"create": 250, "read": 150, "update": 200, "delete": 150}
            max_p95 = {"create": 350, "read": 250, "update": 300, "delete": 250}
            
            assert avg_time < max_avg[operation], f"Performance {operation} non accettabile: media {avg_time:.2f}ms (max {max_avg[operation]}ms)"
            assert p95_time < max_p95[operation], f"Performance {operation} P95 non accettabile: {p95_time:.2f}ms (max {max_p95[operation]}ms)"
            
            logger.info(f"Performance {operation}: avg={avg_time:.2f}ms, p95={p95_time:.2f}ms")
    
    def _run_endpoint_tests(self, client, user_token, benchmark_data):
        results = {}
        headers = {"Authorization": f"Bearer {user_token}"}
        
        for endpoint in benchmark_data["endpoints"]:
            url = endpoint["url"]
            method = endpoint["method"]
            expected_status = endpoint.get("expected_status", 200)
            
            # Esegui warm-up per evitare problemi di cold start
            getattr(client, method)(url, headers=headers)
            
            # Misura tempo di risposta
            times = []
            for _ in range(benchmark_data["repetitions"]):
                start_time = time.time()
                response = getattr(client, method)(url, headers=headers)
                end_time = time.time()
                
                assert response.status_code == expected_status, f"Endpoint {url} failed with status {response.status_code}: {response.text}"
                times.append((end_time - start_time) * 1000)  # ms
            
            # Verifica performance rispetto a soglie definite
            avg_time = statistics.mean(times)
            p95_time = sorted(times)[int(len(times) * 0.95)] if times else 0
            
            max_avg_ms = endpoint.get("max_avg_ms", 200)
            max_p95_ms = endpoint.get("max_p95_ms", 300)
            
            assert avg_time < max_avg_ms, f"Performance non accettabile per {url}: media {avg_time:.2f}ms (max {max_avg_ms}ms)"
            assert p95_time < max_p95_ms, f"Performance P95 non accettabile per {url}: {p95_time:.2f}ms (max {max_p95_ms}ms)"
            
            # Calcola statistiche
            results[url] = self._calculate_stats(times)
        
        return results
    
    def _run_concurrency_tests(self, client, user_token, benchmark_data):
        endpoint = benchmark_data["endpoints"][0]  # Usa primo endpoint
        url = endpoint["url"]
        method = endpoint["method"]
        headers = {"Authorization": f"Bearer {user_token}"}
        
        results = {}
        
        for num_users in benchmark_data["concurrent_users"]:
            # Funzione per worker thread
            def make_request(_):
                start_time = time.time()
                response = getattr(client, method)(url, headers=headers)
                end_time = time.time()
                return {
                    "status": response.status_code,
                    "time": (end_time - start_time) * 1000  # ms
                }
            
            # Esegui richieste concorrenti
            all_results = []
            with ThreadPoolExecutor(max_workers=num_users) as executor:
                all_results = list(executor.map(
                    make_request, 
                    range(num_users * benchmark_data["repetitions"])
                ))
            
            # Verifica status code
            for result in all_results:
                assert result["status"] == endpoint.get("expected_status", 200), f"Request failed with status {result['status']}"
            
            # Calcola statistiche
            times = [result["time"] for result in all_results]
            results[f"concurrent_users_{num_users}"] = self._calculate_stats(times)
            
            # Verifica performance rispetto a soglie scalate per concorrenza
            avg_time = statistics.mean(times)
            p95_time = sorted(times)[int(len(times) * 0.95)] if times else 0
            
            # Soglie scalate in base al numero di utenti concorrenti
            scale_factor = 1 + (num_users / 10)  # Esempio: 5 utenti = fattore 1.5x
            max_avg_ms = endpoint.get("max_avg_ms", 200) * scale_factor
            max_p95_ms = endpoint.get("max_p95_ms", 300) * scale_factor
            
            assert avg_time < max_avg_ms, f"Performance concorrente ({num_users} utenti) non accettabile: media {avg_time:.2f}ms (max {max_avg_ms:.2f}ms)"
            assert p95_time < max_p95_ms, f"Performance P95 concorrente ({num_users} utenti) non accettabile: {p95_time:.2f}ms (max {max_p95_ms:.2f}ms)"
        
        return results
    
    def _run_load_profile_tests(self, client, user_token, benchmark_data):
        results = {}
        loads = [(5, 10), (10, 20), (20, 10)]  # (users, duration)
        headers = {"Authorization": f"Bearer {user_token}"}
        
        for users, duration in loads:
            with ThreadPoolExecutor(max_workers=users) as executor:
                start_time = time.time()
                measurements = []
                
                while time.time() - start_time < duration:
                    futures = [
                        executor.submit(self._make_request, client, url="/api/patterns/", headers=headers)
                        for _ in range(users)
                    ]
                    measurements.extend([f.result() for f in futures])
                
                # Verifica performance sotto carico sostenuto
                avg_time = statistics.mean(measurements)
                p95_time = sorted(measurements)[int(len(measurements) * 0.95)] if measurements else 0
                
                # Definisci soglie in base al carico
                max_avg_ms = 250 * (1 + (users / 20))
                max_p95_ms = 350 * (1 + (users / 20))
                
                assert avg_time < max_avg_ms, f"Performance sotto carico ({users} utenti) non accettabile: media {avg_time:.2f}ms (max {max_avg_ms:.2f}ms)"
                assert p95_time < max_p95_ms, f"Performance P95 sotto carico ({users} utenti) non accettabile: {p95_time:.2f}ms (max {max_p95_ms:.2f}ms)"
                
                results[f"load_{users}users"] = self._calculate_stats(measurements)
        
        return results
    
    def _make_request(self, client, url, headers):
        """Effettua una singola richiesta e misura il tempo."""
        start_time = time.time()
        response = client.get(url, headers=headers)
        end_time = time.time()
        return (end_time - start_time) * 1000  # ms
    
    def _calculate_stats(self, times: List[float]) -> Dict[str, float]:
        """Calcola statistiche di performance complete."""
        if not times:
            return {"min": 0, "max": 0, "avg": 0, "median": 0, "p95": 0, "std_dev": 0}
            
        return {
            "min": min(times),
            "max": max(times),
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "p95": sorted(times)[int(len(times) * 0.95)],
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0
        }
    
    def _validate_and_log_results(self, results: Dict[str, Any], test_name: str):
        """Valida e registra i risultati del test."""
        self._validate_performance_criteria(results)
        self._log_results(results, test_name)
        self._print_summary(results, test_name)
    
    def _validate_performance_criteria(self, results: Dict[str, Any]):
        """Verifica che i risultati soddisfino i criteri di performance."""
        for endpoint, stats in results.items():
            # Utilizziamo assertion per garantire che i test falliscano se le performance sono insufficienti
            assert stats["avg"] < 500, f"Performance troppo bassa per {endpoint}: media {stats['avg']:.2f}ms"
            assert stats["p95"] < 1000, f"Troppi outlier per {endpoint}: P95 {stats['p95']:.2f}ms"
    
    def _log_results(self, results: Dict[str, Any], test_name: str):
        """Salva i risultati in formato JSON."""
        output_dir = Path("performance_results")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"{test_name}_{timestamp}.json"
        
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Risultati performance salvati in {output_file}")
    
    def _print_summary(self, results: Dict[str, Any], test_name: str):
        """Stampa un sommario dettagliato dei risultati."""
        print(f"\n=== Performance Test Results: {test_name} ===")
        for endpoint, stats in results.items():
            print(f"\n{endpoint}:")
            print(f"  Average: {stats['avg']:.2f}ms")
            print(f"  Median: {stats['median']:.2f}ms")
            print(f"  95th percentile: {stats['p95']:.2f}ms")
            print(f"  Min/Max: {stats['min']:.2f}ms / {stats['max']:.2f}ms")
            print(f"  Standard Deviation: {stats['std_dev']:.2f}ms")