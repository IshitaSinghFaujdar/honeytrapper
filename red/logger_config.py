import logging
import sys

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set the lowest level of messages to display
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Send logs to the console
    ]
)

# You can get a logger instance to use in other files
def get_logger(name):
    return logging.getLogger(name)