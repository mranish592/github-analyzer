import logging
import os
import sys
from datetime import datetime

class LoggingUtil:
    def __init__(self):
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging format
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, date_format)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Add file handler for all logs
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Add console handler for INFO and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        root_logger.addHandler(console_handler)
        
        # Add error file handler for ERROR and above
        error_log_file = os.path.join(log_dir, f"error_{datetime.now().strftime('%Y%m%d')}.log")
        error_file_handler = logging.FileHandler(error_log_file)
        error_file_handler.setFormatter(formatter)
        error_file_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_file_handler)
    
    def get_logger(self, name):
        """Get a logger with the specified name."""
        return logging.getLogger(name)

# Create a singleton instance
logging_util = LoggingUtil()

# Export the instance
__all__ = ["logging_util"] 