from logging.handlers import RotatingFileHandler
from config.config import BaseConfig
from flask import Flask, request
import logging
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    # Logging setup
    _log_level = logging.DEBUG if app.config["DEBUG"] else logging.INFO

    # Logging rotate handle
    log_path = app.config["LOGGING_LOCATION"]

    if not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logfile_handler = RotatingFileHandler(
        log_path,
        maxBytes=30 * 1024 * 1024,
        backupCount=5,
        encoding="UTF-8",
    )

    # Logging format handle
    logging_format = logging.Formatter(
        app.config["LOGGING_FORMAT"], datefmt="%Y-%m-%d %H:%M:%S"
    )
    logfile_handler.setFormatter(logging_format)
    app.logger.addHandler(logfile_handler)
    app.logger.setLevel(_log_level)