import logging
from logging.handlers import TimedRotatingFileHandler
import pytz
from datetime import datetime

class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt, datefmt)
        self.tz = tz

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()

def configure_logging():
    singapore_tz = pytz.timezone('Asia/Singapore')

    # Create a TimedRotatingFileHandler for warnings and above
    file_handler = TimedRotatingFileHandler(
        'app.log',
        when='midnight',
        interval=1,
        backupCount=30  # Keep the last 30 days of logs
    )
    file_handler.suffix = "%Y-%m-%d"  # File name will include the date
    file_handler.setLevel(logging.WARNING)  # Set level to WARNING and above
    file_handler.setFormatter(TZFormatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
        datefmt='%Y-%m-%d %H:%M:%S',
        tz=singapore_tz
    ))

    # Create a StreamHandler for debug and info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Set level to DEBUG and above
    console_handler.setFormatter(TZFormatter(
        '%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        tz=singapore_tz
    ))

    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set level to DEBUG for the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Optionally, configure Flask's logger to use the same settings
    logger = logging.getLogger('flask.app')
    logger.setLevel(logging.DEBUG)
    logger.debug("Logging is configured.")

