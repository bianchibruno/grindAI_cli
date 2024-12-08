import logging

# Configure logging
logging.basicConfig(
    filename="logs.txt",           # Log file
    filemode="a",                  # Append mode
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    level=logging.INFO             # Logging level
)

def log_info(message):
    """Log informational messages."""
    logging.info(message)
    print(f"INFO: {message}")  # Also print to console

def log_error(message):
    """Log error messages."""
    logging.error(message)
    print(f"ERROR: {message}")  # Also print to console
