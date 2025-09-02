import logging, datetime

logging.basicConfig(filename=f"log_{datetime.date.today().year}-{datetime.date.today().month}-{datetime.date.today().day}.txt", format='%(levelname)-8s:: %(filename)-8s @ %(asctime)s: %(message)s')
logger = logging.getLogger(__name__)

def init():
    # Define globals
    global cancel_request
    global confiriming_quit
    global basepath
    global json_out
    global logger
    global percent_complete
    
    # Initial values
    cancel_request     = False
    confiriming_quit   = False
    json_out           = False
    logger             = logging.getLogger(__name__)
    percent_complete   = 0