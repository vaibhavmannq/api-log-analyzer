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

if __name__ == "__main__":
    unittest.main()