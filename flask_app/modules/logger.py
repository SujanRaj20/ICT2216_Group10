import logging
from logging.handlers import TimedRotatingFileHandler
import os
import pytz
from pytz import timezone
from datetime import datetime
from flask import Flask, jsonify, request, current_app

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

    # Ensure the logs directory exists
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # Create a TimedRotatingFileHandler for warnings and above
    file_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        when='midnight',
        interval=1,
        backupCount=30  # Keep the last 30 days of logs
    )
    file_handler.prefix = "%Y-%m-%d."  # Log file name format with date
    file_handler.setLevel(logging.INFO)  # Set level to WARNING and above
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
    
    #  # Manually rename the current log file to include the date suffix
    # current_date = datetime.now(singapore_tz).strftime("%Y-%m-%d")
    # initial_log_file = os.path.join(log_dir, f'{current_date}.app.log')
    # if not os.path.exists(initial_log_file):
    #     os.rename(os.path.join(log_dir, 'app.log'), initial_log_file)

    # Test log messages to ensure they are being logged
    root_logger.debug("Debug message test")
    root_logger.info("Info message test")
    root_logger.warning("Warning message test")
    root_logger.error("Error message test")
    root_logger.critical("Critical message test")

def get_log_files(log_dir='logs'):
    """Get a list of log files in the logs directory."""
    current_app.logger.debug(f"get_log_files called")
    return [f for f in os.listdir(log_dir) if f.endswith('.log')]

def get_dates_with_logs(log_dir='logs'):
    """Get a list of dates for which log files are present."""
    current_app.logger.debug(f"get_dates_with_logs called")
    log_files = get_log_files(log_dir)
    
    # Check for 'app.log' and replace with today's date
    dates = {f.split('.')[0] for f in log_files}
    if 'app' in dates:
        today = datetime.now(timezone('Asia/Singapore')).strftime("%Y-%m-%d")
        dates.remove('app')
        dates.add(today)
    
    sorted_dates = sorted(dates)
    current_app.logger.debug(f"dates: {sorted_dates}")
    return sorted_dates

def get_logs_within_date_range(start_date, end_date, log_dir='logs'):
    """Get log files within a specified date range."""
    log_files = get_log_files(log_dir)
    
    today = datetime.now(timezone('Asia/Singapore')).strftime("%Y-%m-%d")
    if 'app.log' in log_files:
        log_files.remove('app.log')
        log_files.append(today + '.log')
    
    selected_files = []
    for log_file in log_files:
        log_date = log_file.split('.')[0]
        if start_date <= log_date <= end_date:
            selected_files.append(log_file)
            
    if today + '.log' in selected_files:
        selected_files.remove(today + '.log')
        selected_files.append('app.log')
    
    return selected_files
