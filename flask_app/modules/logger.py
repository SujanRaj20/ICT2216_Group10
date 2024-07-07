import logging
from logging.handlers import TimedRotatingFileHandler
import os
import pytz
from pytz import timezone
from datetime import datetime
from flask import Flask, jsonify, request, current_app

class TZFormatter(logging.Formatter):   # Custom formatter to include timezone
    def __init__(self, fmt=None, datefmt=None, tz=None):    
        super().__init__(fmt, datefmt)  # Call the base class __init__
        self.tz = tz                    # Set the timezone

    def formatTime(self, record, datefmt=None):                 # Override formatTime
        dt = datetime.fromtimestamp(record.created, self.tz)    # Convert timestamp to datetime
        if datefmt:                                             # If datefmt is specified
            return dt.strftime(datefmt)                         # Return formatted datetime
        else:                                                   # Otherwise
            return dt.isoformat()                               # Return ISO formatted datetime

def configure_logging():                                        # Function to configure logging
    singapore_tz = pytz.timezone('Asia/Singapore')              # Set the timezone to Singapore

    # Ensure the logs directory exists
    log_dir = 'logs'                                            # Set the log directory
    os.makedirs(log_dir, exist_ok=True)                         # Create the log directory if it doesn't exist

    # Create a TimedRotatingFileHandler for warnings and above
    file_handler = TimedRotatingFileHandler(                    # Create a TimedRotatingFileHandler
        os.path.join(log_dir, 'app.log'),                       # join the log directory and log file name to create the log file path
        when='midnight',                                        # Rotate logs at midnight
        interval=1,                                             # Rotate daily
        backupCount=30                                          # Keep the last 30 days of logs
    )
    file_handler.prefix = "%Y-%m-%d."                           # Log file name format with date
    file_handler.setLevel(logging.INFO)                         # Set level to WARNING and above
    file_handler.setFormatter(TZFormatter(                      # Set the formatter with timezone
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',  # set the format for the beginning of the log message
        datefmt='%Y-%m-%d %H:%M:%S',                            # set the date format
        tz=singapore_tz                                         # set the timezone
    ))

    # Create a StreamHandler for debug and info
    console_handler = logging.StreamHandler()                   # Create a StreamHandler
    console_handler.setLevel(logging.DEBUG)                     # Set level to DEBUG and above
    console_handler.setFormatter(TZFormatter(                   # Set the formatter with timezone
        '%(asctime)s %(levelname)s: %(message)s',               # set the format for the beginning of the log message
        datefmt='%Y-%m-%d %H:%M:%S',                            # set the date format
        tz=singapore_tz
    ))

    # Set up the root logger
    root_logger = logging.getLogger()                           # Get the root logger
    root_logger.setLevel(logging.DEBUG)                         # Set level to DEBUG for the root logger
    root_logger.addHandler(file_handler)                        # Add the file handler to the root logger
    root_logger.addHandler(console_handler)                     # Add the console handler to the root logger
    

    # Test log messages to ensure they are being logged
    root_logger.debug("Debug message test")
    root_logger.info("Info message test")
    root_logger.warning("Warning message test")
    root_logger.error("Error message test")
    root_logger.critical("Critical message test")

def get_log_files(log_dir='logs'):                                  # Function to get a list of log files
    """Get a list of log files in the logs directory."""            
    current_app.logger.debug(f"get_log_files called")               # Log a debug message
    return [f for f in os.listdir(log_dir) if f.endswith('.log')]   # Return a list of log files in the logs directory by filtering files that end with '.log' in the directory

def get_dates_with_logs(log_dir='logs'):                            # Function to get a list of dates for which log files are present
    """Get a list of dates for which log files are present."""
    current_app.logger.debug(f"get_dates_with_logs called")         
    log_files = get_log_files(log_dir)                              # Get a list of log files in the logs directory by calling get_log_files
    
    # Check for 'app.log' and replace with today's date
    dates = {f.split('.')[0] for f in log_files}                    # Get the date from the log file name by splitting the file name at the '.' and taking the first part
    if 'app' in dates:                                              # If 'app' is in the dates
        today = datetime.now(timezone('Asia/Singapore')).strftime("%Y-%m-%d")   # Get today's date in the Singapore timezone
        dates.remove('app')                                         # Remove 'app' from the dates
        dates.add(today)                                            # Replace it with today's date
    
    sorted_dates = sorted(dates)                                    # Sort the dates
    current_app.logger.debug(f"dates: {sorted_dates}")      
    return sorted_dates                                             # Return the sorted dates

def get_logs_within_date_range(start_date, end_date, log_dir='logs'):   # Function to get log files within a specified date range
    """Get log files within a specified date range."""
    log_files = get_log_files(log_dir)                                  # Get a list of log files in the logs directory by calling get_log_files
    
    today = datetime.now(timezone('Asia/Singapore')).strftime("%Y-%m-%d")   # Get today's date in the Singapore timezone
    if 'app.log' in log_files:                                              # If 'app.log' is in the log files
        log_files.remove('app.log')                                         # Remove 'app.log'
        log_files.append(today + '.log')                                    # Add today's log file      
    
    selected_files = []                             # Initialize an empty list to store the selected files
    for log_file in log_files:                      # Iterate through the log files
        log_date = log_file.split('.')[0]           # Get the date from the log file name by splitting the file name at the '.' and taking the first part
        if start_date <= log_date <= end_date:      # Check if the log date is within the specified date range
            selected_files.append(log_file)         # Add the log file to the selected files
            
    if today + '.log' in selected_files:            # If today's log file is in the selected files
        selected_files.remove(today + '.log')       # Remove today's log file
        selected_files.append('app.log')            # Add 'app.log' to the selected files
    
    return selected_files                           # Return the selected files
