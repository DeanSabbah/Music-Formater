import logging

logging.basicConfig(filename="log.txt", format='%(levelname)-8s:: %(filename)-8s @ %(asctime)s: %(message)s')


# Quit flags
global cancel_request
global confiriming_quit
# Basic global data
global basepath
global json
#
global logger

def init():
    cancel_request = False
    confiriming_quit = False
    json = False
    logger = logging.getLogger(__name__)