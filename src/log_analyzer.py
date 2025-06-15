import json
import os
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
    most_active_ips = ip_counter.most_common(10)  # Get top 10 instead of 5
    
    # Top 5 API endpoints
    endpoint_counter = Counter(log['endpoint'] for log in valid_logs if 'endpoint' in log)
    top_endpoints = endpoint_counter.most_common(5)
    
    # Flag 5xx errors (server errors)
    errors_5xx = [log for log in valid_logs if 'status' in log and 500 <= log['status'] < 600]
    
    # Flag 4xx errors (client errors) 
    errors_4xx = [log for log in valid_logs if 'status' in log and 400 <= log['status'] < 500]
    
    # All error responses (4xx + 5xx)
    all_errors = errors_4xx + errors_5xx
    
    # Calculate average response time
    response_times = [log['response_time_ms'] for log in valid_logs if 'response_time_ms' in log]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Enhanced endpoint error rate calculation (5xx only as per your original formula)
    endpoint_error_rates = {}
    for endpoint in endpoint_counter:
        server_errors = len([log for log in errors_5xx if log.get('endpoint') == endpoint])
        total_calls = endpoint_counter[endpoint]
        error_rate = (server_errors / total_calls) * 100 if total_calls > 0 else 0
        
        endpoint_error_rates[endpoint] = {
            "total_requests": total_calls,
            "server_errors_5xx": server_errors,
            "error_rate_percent": round(error_rate, 2)
        }
    
    # Status code breakdown
    status_code_counter = Counter(log['status'] for log in valid_logs if 'status' in log)
    
    # Response code analysis
    response_codes = {
        "2xx_success": sum(count for code, count in status_code_counter.items() if 200 <= code < 300),
        "3xx_redirect": sum(count for code, count in status_code_counter.items() if 300 <= code < 400),
        "4xx_client_error": sum(count for code, count in status_code_counter.items() if 400 <= code < 500),
        "5xx_server_error": sum(count for code, count in status_code_counter.items() if 500 <= code < 600)
    }
    
    # Calculate overall error rate using your formula
    total_requests = len(valid_logs)
    server_error_rate = (len(errors_5xx) / total_requests) * 100 if total_requests > 0 else 0
    
    # Top error endpoints (endpoints with most 5xx errors)
    error_endpoint_counter = Counter(log['endpoint'] for log in errors_5xx if 'endpoint' in log)
    top_error_endpoints = error_endpoint_counter.most_common(5)
    
    # Performance insights
    slowest_requests = sorted(
        [log for log in valid_logs if 'response_time_ms' in log and 'endpoint' in log],
        key=lambda x: x['response_time_ms'], 
        reverse=True
    )[:5]  # Get top 5 slowest
    
    # Compile results in a more structured format
    return {
        "metadata": {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_logs_analyzed": len(valid_logs),
            "analysis_period": {
                "start": min(log.get('timestamp', '') for log in valid_logs if log.get('timestamp')),
                "end": max(log.get('timestamp', '') for log in valid_logs if log.get('timestamp'))
            }
        },
        "traffic_analysis": {
            "most_active_ips": [
                {"ip_address": ip, "request_count": count, "percentage": round((count/total_requests)*100, 1)} 
                for ip, count in most_active_ips
            ],
            "top_endpoints": [
                {"endpoint": endpoint, "request_count": count, "percentage": round((count/total_requests)*100, 1)} 
                for endpoint, count in top_endpoints
            ]
        },
        "error_analysis": {
            "server_error_rate_percent": round(server_error_rate, 2),
            "total_server_errors": len(errors_5xx),
            "response_code_summary": response_codes,
            "detailed_status_codes": dict(status_code_counter),
            "top_error_endpoints": [
                {"endpoint": endpoint, "error_count": count} 
                for endpoint, count in top_error_endpoints
            ],
            "endpoint_error_rates": endpoint_error_rates,
            "recent_5xx_errors": [
                {
                    "timestamp": log.get("timestamp", ""),
                    "ip": log.get("ip", ""),
                    "endpoint": log.get("endpoint", ""),
                    "status_code": log.get("status", 0),
                    "method": log.get("method", ""),
                    "response_time_ms": log.get("response_time_ms", 0)
                }
                for log in errors_5xx[:10]  # Show last 10 server errors
            ]
        },
        "performance_analysis": {
            "avg_response_time_ms": round(avg_response_time, 2),
            "slowest_requests": [
                {
                    "endpoint": req.get("endpoint", ""),
                    "response_time_ms": req.get("response_time_ms", 0),
                    "method": req.get("method", ""),
                    "status_code": req.get("status", 0),
                    "ip": req.get("ip", "")
                }
                for req in slowest_requests
            ]
        }
    }

def format_readable_output(results):
    """Format results in a more human-readable format"""
    metadata = results["metadata"]
    traffic = results["traffic_analysis"]
    errors = results["error_analysis"]
    performance = results["performance_analysis"]
    
    now = datetime.fromisoformat(metadata["analysis_timestamp"])
    
    output = []
    output.append("=" * 70)
    output.append(f"🚀 API LOG ANALYSIS REPORT")
    output.append(f"📅 Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 70)
    
    # Summary Section
    output.append(f"\n📊 EXECUTIVE SUMMARY")
    output.append(f"  • Total Requests Analyzed: {metadata['total_logs_analyzed']:,}")
    output.append(f"  • Server Error Rate (5xx): {errors['server_error_rate_percent']}%")
    output.append(f"  • Average Response Time: {performance['avg_response_time_ms']} ms")
    output.append(f"  • Total Server Errors: {errors['total_server_errors']}")
    
    # Traffic Analysis
    output.append(f"\n🌐 TRAFFIC ANALYSIS")
    output.append(f"  Top 5 Most Active IP Addresses:")
    for i, ip_data in enumerate(traffic['most_active_ips'][:5], 1):
        output.append(f"    {i}. {ip_data['ip_address']} → {ip_data['request_count']} requests ({ip_data['percentage']}%)")
    
    output.append(f"\n  🔝 Top 5 API Endpoints:")
    for i, endpoint_data in enumerate(traffic['top_endpoints'], 1):
        output.append(f"    {i}. {endpoint_data['endpoint']} → {endpoint_data['request_count']} requests ({endpoint_data['percentage']}%)")
    
    # Error Analysis
    output.append(f"\n⚠️  ERROR ANALYSIS")
    output.append(f"  Response Code Distribution:")
    codes = errors['response_code_summary']
    output.append(f"    ✅ 2xx (Success): {codes['2xx_success']}")
    output.append(f"    ↗️  3xx (Redirect): {codes['3xx_redirect']}")
    output.append(f"    ❌ 4xx (Client Error): {codes['4xx_client_error']}")
    output.append(f"    🔥 5xx (Server Error): {codes['5xx_server_error']}")
    
    # Server Error Rate by Endpoint
    output.append(f"\n  📈 Server Error Rate by Endpoint (5xx only):")
    sorted_endpoints = sorted(
        errors['endpoint_error_rates'].items(), 
        key=lambda x: x[1]['error_rate_percent'], 
        reverse=True
    )
    for endpoint, data in sorted_endpoints:
        if data['server_errors_5xx'] > 0:
            output.append(f"    • {endpoint}: {data['error_rate_percent']}% " +
                         f"({data['server_errors_5xx']}/{data['total_requests']} requests)")
    
    # Performance Analysis
    output.append(f"\n⚡ PERFORMANCE ANALYSIS")
    output.append(f"  🐌 Slowest Requests (Top 5):")
    for i, req in enumerate(performance['slowest_requests'], 1):
        output.append(f"    {i}. {req['endpoint']} → {req['response_time_ms']} ms " +
                     f"({req['method']} request, Status: {req['status_code']})")
    
    # Recent Server Errors
    if errors['recent_5xx_errors']:
        output.append(f"\n🚨 RECENT SERVER ERRORS (5xx)")
        for i, error in enumerate(errors['recent_5xx_errors'][:5], 1):
            output.append(f"    {i}. {error['endpoint']} → Status {error['status_code']} " +
                         f"({error['method']}) - IP: {error['ip']} - {error['response_time_ms']}ms")
        
        if len(errors['recent_5xx_errors']) > 5:
            output.append(f"    ... and {len(errors['recent_5xx_errors']) - 5} more server errors")
    
    output.append("\n" + "=" * 70)
    output.append("=" * 70)
    
    return "\n".join(output)

def create_output_directory():
    """Create output directory if it doesn't exist"""
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def main():
    # Handle command line arguments
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "sample_api_logs.json"
    
    print(f"🔍 Analyzing log file: {file_path}")
    
    # Load and analyze logs
    logs = load_logs(file_path)
    if not logs:
        print("❌ No valid logs to analyze")
        return
    
    print(f"✅ Loaded {len(logs)} valid log entries")
    
    # Perform analysis
    results = analyze_logs(logs)
    
    # Create output directory
    output_dir = create_output_directory()
    
    # Save JSON results
    json_output_path = os.path.join(output_dir, "analysis_results.json")
    with open(json_output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate and save human-readable report
    readable_output = format_readable_output(results)
    report_output_path = os.path.join(output_dir, "analysis_report.txt")
    with open(report_output_path, "w") as f:
        f.write(readable_output)
    
    # Print human-readable output to console
    print(readable_output)
    
    # Print completion message
    print(f"\n📁 Analysis complete!")
    print(f"   • JSON results: {json_output_path}")
    print(f"   • Human-readable report: {report_output_path}")

if __name__ == "__main__":
    main()