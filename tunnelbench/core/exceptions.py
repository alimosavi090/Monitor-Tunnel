"""
Exception hierarchy for TunnelBench.
"""

class TunnelBenchError(Exception):
    """Base exception for all TunnelBench errors."""
    pass

class ConfigurationError(TunnelBenchError):
    """Raised when there is an issue with the configuration file."""
    pass

class NetworkError(TunnelBenchError):
    """Raised when a network operation fails."""
    pass

class BenchmarkError(TunnelBenchError):
    """Raised when a benchmarking operation fails."""
    pass

class ReportGenerationError(TunnelBenchError):
    """Raised when report generation fails."""
    pass
