import logging
import os
from datetime import datetime

from colorlog import ColoredFormatter

from setup import LOGS_PATH

if not LOGS_PATH:
    LOGS_PATH = os.getcwd() + "/logs"
    if not os.path.exists(LOGS_PATH):
        os.mkdir(LOGS_PATH)


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOG_FORMAT)
logging.basicConfig(filename=f'{LOGS_PATH}/{datetime.now()}.log')
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
log = logging.getLogger('pythonConfig')
log.setLevel(LOG_LEVEL)
log.addHandler(stream)
