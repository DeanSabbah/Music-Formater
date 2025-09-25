from pathlib import Path

import logging, datetime

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(filename=f"logs/log_{datetime.date.today().year}-{datetime.date.today().month}-{datetime.date.today().day}.txt", format='%(levelname)-8s:: %(filename)-8s @ %(asctime)s: %(message)s')

message_box                 = None
display_message_box:bool    = False
cancel_request:bool         = False
confiriming_quit:bool       = False
basepath:str                = ""
json_out:bool               = False
logger:logging.Logger       = logging.getLogger(__name__)
percent_complete:float      = 0

class log:
    def _write_to_message_box(self, message: str) -> None:
        if not message_box or not display_message_box:
            return
        
        message_box["state"] = "normal"
        message_box.insert("end", str(message) + "\n")
        message_box["state"] = "disabled"
        message_box.see("end")

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