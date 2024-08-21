# Create a custom logger and set it up. To use this logger, we'll import this file
# Doing this'll set up the configuration on the other file.
# It also contains a function used to build an id, that will be at the beggining
# of the log message.

import logging
import datetime as dt

today = dt.datetime.today()
debug_filename = f"logs/debug_{today:%y}{today.month:02d}{today.day:02d}.log"
error_filename = f"logs/error_{today:%y}{today.month:02d}{today.day:02d}.log"

# Create a custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set the root logger level to INFO

# Create handlers
debug_handler = logging.FileHandler(debug_filename)  # Save on a file
debug_handler.setLevel(logging.DEBUG)

error_handler = logging.FileHandler(error_filename)  # Save on a file
error_handler.setLevel(logging.ERROR)

stream_handler = logging.StreamHandler()  # Print to console

# Create formatters and add them to the handlers
formatter = logging.Formatter("%(asctime)s - %(levelname)-8s -> %(message)s")
debug_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(debug_handler)
logger.addHandler(error_handler)
logger.addHandler(stream_handler)


# Build an id to know which delegation, lote and finca is being processed.
def build_id(delegation: int, lote: int = ".", finca: int = "."):
    s_delegation = str(delegation)
    s_lote = str(lote)
    s_finca = str(finca)
    return f"{s_delegation:^4}- {s_lote:^4}- {s_finca:^4} - "