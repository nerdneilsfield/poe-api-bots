import logging
import coloredlogs
from typing import Optional

class GlobalLoggerManager:
    _instance = None
    _logger = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GlobalLoggerManager()
        return cls._instance

    def __init__(self):
        if GlobalLoggerManager._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger('global_logger')
        logger.setLevel(logging.INFO)
        
        coloredlogs.install(
            level='INFO', 
            logger=logger,
            fmt='%(asctime)s | %(levelname)8s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
        )
        
        GlobalLoggerManager._logger = logger

    def get_logger(self, name: Optional[str] = None):
        return logging.getLogger(name or 'global_logger')

def get_logger(name: Optional[str] = None):
    return GlobalLoggerManager.get_instance().get_logger(name) 