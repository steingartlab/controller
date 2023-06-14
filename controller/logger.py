"""Logger config."""

import logging
import os

LOG_FILENAME = "logs/logs.log"

def configure() -> None:
    os.makedirs(
        os.path.dirname(LOG_FILENAME),
        exist_ok=True
    )
    logging.basicConfig(
        filename=LOG_FILENAME,
        level=logging.INFO,
        format='%(asctime)s: %(message)s'
    )