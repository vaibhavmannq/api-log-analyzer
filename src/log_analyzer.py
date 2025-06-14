import json
from collections import Counter
from datetime import datetime
import sys

def load_logs(file_path):
    """Load and parse log data from JSON file"""
    try:
        with open(file_path, 'r') as file:
            logs = json.load(file)
            # Filter out incomplete log entries
            return [log for log in logs if isinstance(log, dict) and 'ip' in log and 'endpoint' in log]
    except Exception as e:
        print(f"Error loading log file: {e}")
        return []

def analyze_logs(logs):
    """Analyze log data and generate insights"""
    # Skip incomplete log entries
    valid_logs = [log for log in logs if isinstance(log, dict) and 'ip' in log]
    
    # Most active IPs
    ip_counter = Counter(log['ip'] for log in valid_logs if 'ip' in log)
    most_active_ips = ip_counter.most_common(5)
    
    # Top 5 API endpoints
    endpoint_counter = Counter(log['endpoint'] for log in valid_logs if 'endpoint' in log)
    top_endpoints = endpoint_counter.most_common(5)
    
    # Flag 5xx errors
    errors_5xx = [log for log in valid_logs if 'status' in log and 500 <= log['status'] < 600]
    
    # Calculate average response time
    response_times = [log['response_time_ms'] for log in valid_logs if 'response_time_ms' in log]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Add error rate calculation
    endpoint_error_rates = {}
    for endpoint in endpoint_counter:
        errors = len([log for log in errors_5xx if log.get('endpoint') == endpoint])
        calls = endpoint_counter[endpoint]
        endpoint_error_rates[endpoint] = {
            "calls": calls,
            "errors": errors,
            "error_rate": round((errors/calls)*100, 2) if calls > 0 else 0
        }
    
    # Compile results
    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "total_logs_analyzed": len(valid_logs),
        "most_active_ips": [{"ip": ip, "count": count} for ip, count in most_active_ips],
        "top_endpoints": [{"endpoint": endpoint, "count": count} for endpoint, count in top_endpoints],
        "error_summary": {
            "5xx_count": len(errors_5xx),
            "5xx_errors": [
                {
                    "timestamp": log.get("timestamp", ""),
                    "ip": log.get("ip", ""),
                    "endpoint": log.get("endpoint", ""),
                    "status": log.get("status", 0),
                    "method": log.get("method", "")
                }
                for log in errors_5xx
            ]
        },
        "endpoint_error_rates": endpoint_error_rates,
        "avg_response_time_ms": round(avg_response_time, 2)
    }

def format_readable_output(results):
    """Format results in a more human-readable format"""
    now = datetime.fromisoformat(results["analysis_timestamp"])
    
    output = []
    output.append("=" * 60)
    output.append(f"API LOG ANALYSIS REPORT - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 60)
    output.append(f"\n📊 SUMMARY")
    output.append(f"  Total Logs Analyzed: {results['total_logs_analyzed']}")
    output.append(f"  Average Response Time: {results['avg_response_time_ms']} ms")
    output.append(f"  Server Errors (5xx): {results['error_summary']['5xx_count']}")
    
    output.append(f"\n🔝 TOP 5 ENDPOINTS")
    for i, endpoint in enumerate(results['top_endpoints'], 1):
        output.append(f"  {i}. {endpoint['endpoint']} - {endpoint['count']} requests")
    
    output.append(f"\n🖥️ MOST ACTIVE IPs")
    for i, ip in enumerate(results['most_active_ips'], 1):
        output.append(f"  {i}. {ip['ip']} - {ip['count']} requests")
    
    if 'endpoint_error_rates' in results:
        output.append(f"\n⚠️ ENDPOINT ERROR RATES")
        # Sort by error rate (highest first)
        sorted_endpoints = sorted(
            results['endpoint_error_rates'].items(), 
            key=lambda x: x[1]['error_rate'], 
            reverse=True
        )
        for endpoint, data in sorted_endpoints:
            if data['errors'] > 0:
                output.append(f"  {endpoint}: {data['error_rate']}% ({data['errors']}/{data['calls']})")
    
    output.append(f"\n❌ SERVER ERRORS (5xx)")
    errors = results['error_summary']['5xx_errors']
    if not errors:
        output.append("  No server errors detected")
    else:
        for i, error in enumerate(errors[:5], 1):  # Show first 5 errors
            if 'endpoint' in error and error['endpoint']:
                output.append(f"  {i}. {error['endpoint']} - Status {error['status']} - IP: {error['ip']}")
        
        if len(errors) > 5:
            output.append(f"  ... and {len(errors) - 5} more errors")
    
    output.append("\n" + "=" * 60)
    return "\n".join(output)

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_api_logs.json"
    
    logs = load_logs(file_path)
    if not logs:
        print("No valid logs to analyze")
        return
    
    results = analyze_logs(logs)
    
    # Output to console and file
    print(json.dumps(results, indent=2))
    
    with open("analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print human-readable output
    readable_output = format_readable_output(results)
    print(readable_output)
    
    print(f"Analysis complete. Results saved to analysis_results.json")

if __name__ == "__main__":
    main()