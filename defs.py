import logging, datetime

logging.basicConfig(filename=f"log_{datetime.date.today().year}-{datetime.date.today().month}-{datetime.date.today().day}.txt", format='%(levelname)-8s:: %(filename)-8s @ %(asctime)s: %(message)s')
logger = logging.getLogger(__name__)

message_box = None

def init():
    # Define globals
    global cancel_request   # noqa
    global confiriming_quit # noqa
    global basepath         # noqa
    global json_out         # noqa
    global logger           # noqa
    global percent_complete # noqa
    
    # Initial values
    cancel_request     = False
    confiriming_quit   = False
    json_out           = False
    logger             = logging.getLogger(__name__)
    percent_complete   = 0

class log:
    def _write_to_message_box(self, message: str) -> None:
        mb = globals().get("message_box")
        if not mb:
            return
        
        mb["state"] = "normal"
        mb.insert("end", str(message) + "\n")
        mb["state"] = "disabled"
        mb.see("end")

    def debug(self, message: str):
        self._write_to_message_box(message)
        logger.debug(message)
        
    def info(self, message: str):
        self._write_to_message_box(message)
        logger.info(message)
        
    def warning(self, message: str):
        self._write_to_message_box(message)
        logger.warning(message)
        
    def error(self, message: str):
        self._write_to_message_box(message)
        logger.error(message)
        
    def fatal(self, message: str):
        self._write_to_message_box(message)
        logger.fatal(message)