"""
Logger configuration using Rich.
"""
import logging
from rich.logging import RichHandler

def setup_logger(debug: bool = False, verbose: bool = False) -> logging.Logger:
    """
    Configure and return the global logger.
    
    Args:
        debug: If True, set level to DEBUG.
        verbose: If True, set level to INFO (if debug is False).
    """
    level = logging.WARNING
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
        
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)]
    )
    
    logger = logging.getLogger("tunnelbench")
    return logger

# Default logger instance
log = setup_logger()
