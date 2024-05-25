import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)-8s - %(name)-20s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    filename='4Queens.log',
    filemode='w'
)

def get_logger(name):
    return logging.getLogger(name)
