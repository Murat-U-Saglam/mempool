import logging
import os
from functools import wraps

def setup_logger(name=None, log_file='application.log', level=logging.DEBUG):
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        logger.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
    
    return logger

