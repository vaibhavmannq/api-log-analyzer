import unittest
import json
import sys
import os

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.log_analyzer import load_logs, analyze_logs

class TestLogAnalyzer(unittest.TestCase):
    def test_load_logs(self):
        """Test that logs can be loaded from a file"""
        logs = load_logs("data/sample_api_logs.json")
        self.assertTrue(len(logs) > 0)
        
    def test_analyze_logs(self):
        """Test log analysis functionality"""
        sample_logs = [
            {"ip": "192.168.1.1", "endpoint": "/api/test", "status": 200, "response_time_ms": 100},
            {"ip": "192.168.1.1", "endpoint": "/api/test", "status": 200, "response_time_ms": 200},
            {"ip": "192.168.1.2", "endpoint": "/api/other", "status": 500, "response_time_ms": 300},
        ]
        
        results = analyze_logs(sample_logs)
        
        # Check that the analysis contains expected fields
        self.assertIn("most_active_ips", results)
        self.assertIn("top_endpoints", results)
        self.assertIn("error_summary", results)
        
        # Check error detection
        self.assertEqual(results["error_summary"]["5xx_count"], 1)
        
        # Check IP counting
        ips = {ip["ip"]: ip["count"] for ip in results["most_active_ips"]}
        self.assertEqual(ips["192.168.1.1"], 2)
        self.assertEqual(ips["192.168.1.2"], 1)
        
        # Check endpoint counting
        endpoints = {ep["endpoint"]: ep["count"] for ep in results["top_endpoints"]}
        self.assertEqual(endpoints["/api/test"], 2)
        self.assertEqual(endpoints["/api/other"], 1)
    
    def test_status_code_distribution(self):
        """Test status code distribution functionality"""
        sample_logs = [
            {"ip": "192.168.1.1", "endpoint": "/api/test", "status": 200, "response_time_ms": 100},
            {"ip": "192.168.1.1", "endpoint": "/api/test", "status": 301, "response_time_ms": 200},
            {"ip": "192.168.1.2", "endpoint": "/api/other", "status": 404, "response_time_ms": 300},
            {"ip": "192.168.1.3", "endpoint": "/api/test", "status": 500, "response_time_ms": 400},
        ]
        
        results = analyze_logs(sample_logs)
        
        # Check status code distribution
        self.assertIn("status_code_distribution", results)
        status_codes = results["status_code_distribution"]
        self.assertEqual(status_codes["2xx"], 1)
        self.assertEqual(status_codes["3xx"], 1)
        self.assertEqual(status_codes["4xx"], 1)
        self.assertEqual(status_codes["5xx"], 1)
    
    def test_endpoint_error_rates(self):
        """Test endpoint error rates calculation"""
        sample_logs = [
            {"ip": "192.168.1.1", "endpoint": "/api/test", "status": 200, "response_time_ms": 100},
            {"ip": "192.168.1.1", "endpoint": "/api/test", "status": 500, "response_time_ms": 200},
            {"ip": "192.168.1.2", "endpoint": "/api/test", "status": 200, "response_time_ms": 300},
            {"ip": "192.168.1.3", "endpoint": "/api/other", "status": 500, "response_time_ms": 400},
        ]
        
        results = analyze_logs(sample_logs)
        
        # Check endpoint error rates
        self.assertIn("endpoint_error_rates", results)
        error_rates = results["endpoint_error_rates"]
        
        self.assertEqual(error_rates["/api/test"]["calls"], 3)
        self.assertEqual(error_rates["/api/test"]["errors"], 1)
        self.assertEqual(error_rates["/api/test"]["error_rate"], 33.33)
        
        self.assertEqual(error_rates["/api/other"]["calls"], 1)
        self.assertEqual(error_rates["/api/other"]["errors"], 1)
        self.assertEqual(error_rates["/api/other"]["error_rate"], 100.0)
    
    def test_slowest_requests(self):
        """Test slowest requests tracking"""
        sample_logs = [
            {"ip": "192.168.1.1", "endpoint": "/api/fast", "status": 200, "response_time_ms": 100},
            {"ip": "192.168.1.1", "endpoint": "/api/slow", "status": 200, "response_time_ms": 950},
            {"ip": "192.168.1.2", "endpoint": "/api/medium", "status": 200, "response_time_ms": 500},
            {"ip": "192.168.1.3", "endpoint": "/api/slower", "status": 200, "response_time_ms": 800},
            {"ip": "192.168.1.4", "endpoint": "/api/slowest", "status": 200, "response_time_ms": 1000},
            {"ip": "192.168.1.5", "endpoint": "/api/quick", "status": 200, "response_time_ms": 50},
        ]
        
        results = analyze_logs(sample_logs)
        
        # Check slowest requests
        self.assertIn("slowest_requests", results)
        slowest = results["slowest_requests"]
        
        # Should have 5 slowest requests (or fewer if fewer logs)
        self.assertEqual(len(slowest), 5)
        
        # Check order (should be descending by response time)
        self.assertEqual(slowest[0]["endpoint"], "/api/slowest")
        self.assertEqual(slowest[1]["endpoint"], "/api/slow")
        self.assertEqual(slowest[2]["endpoint"], "/api/slower")
        self.assertEqual(slowest[3]["endpoint"], "/api/medium")
        self.assertEqual(slowest[4]["endpoint"], "/api/fast")
        
        # Check the fastest one isn't included (since we only track top 5)
        found_quick = False
        for req in slowest:
            if req["endpoint"] == "/api/quick":
                found_quick = True
        self.assertFalse(found_quick)

if __name__ == "__main__":
    unittest.main()