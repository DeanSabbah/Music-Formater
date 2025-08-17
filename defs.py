import logging

logging.basicConfig(filename="log.txt", format='%(levelname)-8s:: %(filename)-8s @ %(asctime)s: %(message)s')
logger = logging.getLogger(__name__)

def init():
    global cancel_request  # noqa
    cancel_request = False
    global confiriming_quit  # noqa
    confiriming_quit = False
    global basepath  # noqa
    global json  # noqa
    json = False
    global logger  # noqa
    logger = logging.getLogger(__name__)