import logging

logging.basicConfig(filename="log.txt", format='%(levelname)-8s:: %(filename)-8s @ %(asctime)s: %(message)s')
logger = logging.getLogger(__name__)


def init(log_name:str=""):
    # Quit flags
    global cancel_request
    cancel_request = False
    global confiriming_quit
    confiriming_quit = False
    # Basic global data
    global basepath
    global json
    json = False
    #
    global logger
    logger = logging.getLogger(__name__)