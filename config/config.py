class BaseConfig(object):
    # Service
    DEBUG = False
    PORT = 5000
    HOST = "0.0.0.0"

    # Logging
    LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGGING_LOCATION = "./log/url/url.log"

    #Database
    SQLITE_PATH = "./db/urls.db"