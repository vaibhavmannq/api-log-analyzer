# API Log Analyzer

A simple Python tool that analyzes API logs and generates insights about traffic patterns and errors.

## Project Purpose

This tool scans API log files (in JSON format) to help you understand:
- Which IP addresses are making the most requests
- Which API endpoints are most frequently accessed
- Where server errors (5xx) are occurring
- Average response times for your API

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
API LOG ANALYSIS REPORT - 2025-06-14 12:34:56
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

⚠️ ENDPOINT ERROR RATES
  /api/login: 33.33% (2/6)
  /api/orders: 11.11% (1/9)
```