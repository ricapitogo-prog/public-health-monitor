import logging
from datetime import datetime
import os

def setup_logger(name: str) -> logging.Logger:
    """
    Create a logger that writes to both file and console
    Args:
        name: Name of the logger (usually __name__ from calling file)
    Returns:
        Configured logger object
    """
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # File handler - writes everything to file
    log_file = f'logs/health_monitor_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler - only important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Test it
if __name__ == '__main__':
    logger = setup_logger(__name__)
    
    logger.debug("This is a debug message (only in file)")
    logger.info("Fetching public health data...")
    logger.warning("Daily cases increased by 10%")
    logger.error("API request failed")
    
    print("\n✓ Check the logs/ folder for the log file")