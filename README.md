# API Log Analyzer

A simple Python tool that analyzes API logs and generates insights about traffic patterns, errors, and performance metrics.

## Project Purpose

This tool scans API log files (in JSON format) to help you understand:
- Which IP addresses are making the most requests
- Which API endpoints are most frequently accessed
- Detailed error analysis including response code distribution
- Performance metrics including average response times and slowest requests
- Error rates by endpoint to identify problematic services

## Features

- **Traffic Analysis**: Most active IPs and popular endpoints
- **Error Analysis**: 
  - Response code distribution (2xx, 3xx, 4xx, 5xx)
  - Error rates by endpoint
  - Detailed server error logs
- **Performance Analysis**:
  - Average response time
  - Top 5 slowest requests with details
  - Performance by endpoint

## Getting Started

### Prerequisites
- Python 3.6 or higher

### Project Structure
```
api-log-analyzer/
├── src/             # Core analysis logic
├── tests/           # Unit tests
├── data/            # Input log files
├── output/          # Analysis results
├── main.py          # Entry point
└── README.md
```

### Installation
1. Clone this repository
2. Place your API logs in JSON format in the `data/` directory

### Running the Analyzer
```bash
# Run with default sample file (data/sample_api_logs.json)
python main.py

# Or specify a custom log file
python main.py path/to/your/logs.json
```

### Running Tests
```bash
# Run the unit tests
python -m unittest tests/test_analyzer.py
```

## Output
The analyzer produces:
1. A formatted report in the console
2. A detailed JSON file in the `output/` directory

## Sample Console Output
```
============================================================
API LOG ANALYSIS REPORT
============================================================

📊 SUMMARY
  Total Logs Analyzed: 50
  Average Response Time: 530.74 ms
  Server Errors (5xx): 13

🔝 TOP 5 ENDPOINTS
  1. /api/logout - 18 requests
  2. /api/orders - 9 requests
  3. /api/users - 9 requests
  ...

🖥️ MOST ACTIVE IPs
  1. 83.144.94.57 - 1 requests
  2. 146.24.177.177 - 1 requests
  ...

⚠️ ERROR ANALYSIS
  Response Code Distribution:
    ✅ 2xx (Success): 7
    ↗️ 3xx (Redirect): 0
    ❌ 4xx (Client Error): 30
    🔥 5xx (Server Error): 13

  📈 Server Error Rate by Endpoint (5xx only):
    • /api/data: 50.0% (4/8 requests)
    • /api/login: 33.33% (2/6 requests)
    • /api/logout: 22.22% (4/18 requests)
    • /api/orders: 22.22% (2/9 requests)
    • /api/users: 11.11% (1/9 requests)

⚡ PERFORMANCE ANALYSIS
  🐌 Slowest Requests (Top 5):
    1. /api/orders → 992 ms (DELETE request, Status: 400)
    2. /api/orders → 992 ms (PUT request, Status: 403)
    3. /api/users → 946 ms (PUT request, Status: 403)
    4. /api/logout → 943 ms (PUT request, Status: 400)
    5. /api/logout → 918 ms (POST request, Status: 404)

❌ SERVER ERRORS (5xx)
  1. /api/logout - Status 500 - IP: 37.217.17.177
  2. /api/data - Status 500 - IP: 146.24.177.177
  ...and 11 more errors
============================================================
```