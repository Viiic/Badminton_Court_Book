import logging

def get_logger(logger_name, file_name):
    logger = logging.getLogger(logger_name)  
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(file_name)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger