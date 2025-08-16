import logging

logger = logging.getLogger(__name__)


def init(log_name:str=""):
    global log_out
    log_out = log_name
    if log_name != "":
        logging.basicConfig(filename=log_name, level=logging.ERROR)
    global basepath
    global json
    json = False