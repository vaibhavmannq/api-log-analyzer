# Export key functions at the package level
from .log_analyzer import load_logs, analyze_logs, format_readable_output

__all__ = ['load_logs', 'analyze_logs', 'format_readable_output']