import logging
import sys

def setup_logger():
    """
    Configures the logging settings for the application. The logging behavior 
    is adjusted based on whether the application is running as a PyInstaller 
    bundle or in a standard Python environment.
    """
    if getattr(sys, 'frozen', False):
        # The application is running as a PyInstaller bundle
        logging.basicConfig(
            level=logging.CRITICAL,
            format='%(asctime)s - %(levelname)-8s - %(name)-20s - %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p'
        )
    else:
        # The application is running in a normal Python environment
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)-8s - %(name)-20s - %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            filename='4Queens.log',
            filemode='w'
        )

def get_logger(name):
    """
    Retrieves a logger with the specified name.

    Args:
        name (str): The name of the logger to retrieve.

    Returns:
        logging.Logger: The configured logger instance.
    """
    return logging.getLogger(name)
