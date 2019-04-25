"""
Logging Configuration
"""

import logging
import logging.config
import yaml

from pathlib import WindowsPath
project_folder = WindowsPath(r'C:\Users\TheoI\OneDrive\Documents\Python Projects\Shocal')

with open(project_folder / 'log config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)
