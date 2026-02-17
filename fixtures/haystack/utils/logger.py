# Just noise
def create_logger(name):
    import logging
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
