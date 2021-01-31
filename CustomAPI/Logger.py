import logging

def defaultLogging():
    logger = logging.getLogger("BookletsGeneration")
    format = '%(asctime)s [%(levelname)s] %(message)s'
    formatter = logging.Formatter(format)
    logging.basicConfig(level=logging.DEBUG, format=format, datefmt='%d/%m/%Y %H:%M:%S', filename="_log/debug.log")
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    ch2 = logging.FileHandler("_log/warning.log")
    ch2.setLevel(logging.WARNING)
    ch2.setFormatter(formatter)
    logging.getLogger('').addHandler(ch)
    logging.getLogger('').addHandler(ch2)