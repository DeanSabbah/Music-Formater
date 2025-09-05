from typing import cast
from tkinter import Tk
import pytest

import app, defs, logging

class DummyExecutor:
    def __init__(self):
        self.shutdown_called = False
    def shutdown(self, wait=False, cancel_futures=False):
        self.shutdown_called = True

def test_switch(monkeypatch):
    defs.json_out = False

    app.switch_json()
    assert defs.json_out is True
    app.switch_json()
    assert defs.json_out is False
    
def test_log(monkeypatch):
    log_levels = { "Debug":logging.DEBUG, "Info":logging.INFO, "Warning":logging.WARNING, "Error":logging.ERROR, "Critical":logging.CRITICAL }
    
    app.set_log_level("Off")
    assert defs.logger.disabled is True

    for name, level in log_levels.items():
        app.set_log_level(name)
        
        assert defs.logger.disabled == False
        assert defs.logger.level == level
        
def test_close_shuts_down_executor(monkeypatch):
    app.executor = DummyExecutor()
    app.ui = app.user_interface()
    
    class RootStub:
        destroyed = False
        def destroy(self): self.destroyed = True
    app.ui.root = cast(Tk, RootStub())

    app.close()
    assert defs.cancel_request is True
    assert app.executor.shutdown_called
    assert app.ui.root.destroyed # type: ignore[assignment]
    
def test_on_closing_confirmed(monkeypatch):
    called = {}

    monkeypatch.setattr(app, "close", lambda: called.setdefault("closed", True))
    monkeypatch.setattr("tkinter.messagebox.askokcancel", lambda title, msg: True)
    app.on_closing()
    
    assert called.get("closed") is True

def test_on_closing_cancelled(monkeypatch):
    called = {}
    monkeypatch.setattr(app, "close", lambda: called.setdefault("closed", True))
    monkeypatch.setattr("tkinter.messagebox.askokcancel", lambda title, msg: False)
    app.on_closing()
    
    assert called.get("closed") is None