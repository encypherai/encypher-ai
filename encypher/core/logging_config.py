import logging

from rich.logging import RichHandler

# Configuration
LOG_LEVEL = logging.INFO  # Default level, can be overridden by env var later
LOG_FORMAT = "%(message)s"
DATE_FORMAT = "[%X]"  # Use Rich's default time format

# Create RichHandler
# show_path=False prevents logging the source file path, which can be noisy
# rich_tracebacks=True enables pretty tracebacks for exceptions
rich_handler = RichHandler(show_path=False, rich_tracebacks=True, markup=True, log_time_format=DATE_FORMAT)

# Configure a specific logger for the encypher library
# Avoids conflicts if the user application also configures the root logger
logger = logging.getLogger("encypher")
logger.setLevel(LOG_LEVEL)

# Add the RichHandler only to this specific logger
# Check if handlers are already added to prevent duplicates during reloads
if not any(isinstance(h, RichHandler) for h in logger.handlers):
    logger.addHandler(rich_handler)

# Prevent the encypher logger from propagating messages to the root logger
# This ensures only our RichHandler formats encypher messages
logger.propagate = False


# Example usage (within other modules):
# from .logging_config import logger
# logger.info("This is an info message.")
# logger.warning("This is a warning.")
# try:
#     1 / 0
# except ZeroDivisionError:
#     logger.exception("An error occurred")
