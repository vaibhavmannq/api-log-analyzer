import sys
import json
from src import load_logs, analyze_logs, format_readable_output

def main():
    """Entry point for the API Log Analyzer"""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/sample_api_logs.json"
    
    logs = load_logs(file_path)
    if not logs:
        print("No valid logs to analyze")
        return
    
    results = analyze_logs(logs)
    
    # Save JSON results to file
    with open("output/analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print human-readable format to console
    print(format_readable_output(results))
    print(f"\nAnalysis complete. Full results saved to output/analysis_results.json")

if __name__ == "__main__":
    main()