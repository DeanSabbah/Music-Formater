import logging

logging.basicConfig(filename="log.txt", format='%(levelname)-8s:: %(filename)-8s @ %(asctime)s: %(message)s')
logger = logging.getLogger(__name__)

def init():
    global cancel_request  # noqa
    global confiriming_quit  # noqa
    global basepath  # noqa
    global json  # noqa
    global logger  # noqa
    global percent_complete
    
    cancel_request = False
    confiriming_quit = False
    json = False
    logger = logging.getLogger(__name__)
    percent_complete = 0