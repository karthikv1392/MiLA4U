import logging
import logging.handlers
import time
from configparser import ConfigParser

CONFIGURATION_FILE = "settings.conf"
parser = ConfigParser()
parser.read(CONFIGURATION_FILE)
LOG_PATH = parser.get('settings', 'log_path')
PROJECT_NAME = parser.get("settings", "project_name")
LOG_FILE = LOG_PATH + PROJECT_NAME

logger = logging.getLogger(PROJECT_NAME)
log_handler = logging.FileHandler(LOG_FILE + "_" + time.strftime("%Y%m%d")+'.log')
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',"%Y-%m-%d %H:%M:%S")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
logger.debug('Logger Initialized')
