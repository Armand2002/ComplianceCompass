# tests/performance/test_api_performance.py
"""
Test di performance per API endpoints critici.

Misura tempi di risposta e throughput per scenari di uso comune.
"""
import pytest
import time
import statistics
import json
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from pathlib import Path

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
                {"url": "/api/patterns/", "method": "get"},
                {"url": "/api/search/patterns?q=test", "method": "get"},
                {"url": "/api/health/", "method": "get"}
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
    
    def _run_endpoint_tests(self, client, user_token, benchmark_data):
        results = {}
        headers = {"Authorization": f"Bearer {user_token}"}
        
        for endpoint in benchmark_data["endpoints"]:
            url = endpoint["url"]
            method = endpoint["method"]
            
            # Esegui warm-up per evitare problemi di cold start
            getattr(client, method)(url, headers=headers)
            
            # Misura tempo di risposta
            times = []
            for _ in range(benchmark_data["repetitions"]):
                start_time = time.time()
                response = getattr(client, method)(url, headers=headers)
                end_time = time.time()
                
                assert response.status_code == 200, f"Endpoint {url} failed with status {response.status_code}"
                times.append((end_time - start_time) * 1000)  # ms
            
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
                assert result["status"] == 200, f"Request failed with status {result['status']}"
            
            # Calcola statistiche
            times = [result["time"] for result in all_results]
            results[num_users] = self._calculate_stats(times)
        
        return results
    
    def _run_load_profile_tests(self, client, user_token, benchmark_data):
        results = {}
        loads = [(5, 10), (10, 20), (20, 10)]  # (users, duration)
        
        for users, duration in loads:
            with ThreadPoolExecutor(max_workers=users) as executor:
                start_time = time.time()
                measurements = []
                
                while time.time() - start_time < duration:
                    futures = [
                        executor.submit(self._make_request, client, user_token)
                        for _ in range(users)
                    ]
                    measurements.extend([f.result() for f in futures])
                
                results[f"load_{users}users"] = self._calculate_stats(measurements)
        
        return results
    
    def _make_request(self, client, user_token):
        """Effettua una singola richiesta e misura il tempo."""
        headers = {"Authorization": f"Bearer {user_token}"}
        start_time = time.time()
        response = client.get("/api/patterns/", headers=headers)
        end_time = time.time()
        return (end_time - start_time) * 1000  # ms
    
    def _calculate_stats(self, times: List[float]):
        """Calcola statistiche di performance."""
        return {
            "min": min(times),
            "max": max(times),
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "p95": sorted(times)[int(len(times) * 0.95)]
        }
    
    def _validate_and_log_results(self, results: Dict[str, Any], test_name: str):
        """Valida e registra i risultati del test."""
        self._validate_performance_criteria(results)
        self._log_results(results, test_name)
        self._print_summary(results, test_name)
    
    def _validate_performance_criteria(self, results: Dict[str, Any]):
        """Verifica che i risultati soddisfino i criteri di performance."""
        for endpoint, stats in results.items():
            assert stats["avg"] < 200, f"Performance non accettabile per {endpoint}"
            assert stats["p95"] < 300, f"Troppi outlier per {endpoint}"
    
    def _log_results(self, results: Dict[str, Any], test_name: str):
        """Salva i risultati in formato JSON."""
        output_dir = Path("performance_results")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / f"{test_name}_{time.strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(results, f, indent=2)
    
    def _print_summary(self, results: Dict[str, Any], test_name: str):
        """Stampa un sommario dei risultati."""
        print(f"\n=== Performance Test Results: {test_name} ===")
        for endpoint, stats in results.items():
            print(f"\n{endpoint}:")
            print(f"  Average: {stats['avg']:.2f}ms")
            print(f"  95th percentile: {stats['p95']:.2f}ms")
            print(f"  Min/Max: {stats['min']:.2f}ms / {stats['max']:.2f}ms")