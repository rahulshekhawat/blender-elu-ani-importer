#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614

"""
This module contains functionality to add and save logs to files
"""

import os
import enum
from commonfunctions import get_current_time_as_string


class FileLogger:

    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._log_file_path = get_current_time_as_string()
        # Replace all spaces and semicolons in FileName with hyphen
        self._log_file_path = self._log_file_path.replace(' ', '-')
        self._log_file_path = self._log_file_path.replace(':', '-')
        self._log_file_path += '.md'
        self._log_file_path = os.getcwd() + os.sep + 'logs' + os.sep + self._log_file_path
        self._log_file_stream = open(self._log_file_path, 'a+')

    def __del__(self):
        self._log_file_stream.close()

    def log_info(self, log_string: str):
        log_message = "[" + get_current_time_as_string() + "] " + "[LOG]" + log_string
        self._log_file_stream.write(log_message)
        self._log_file_stream.flush()

    def log_warning(self, log_string: str):
        log_message = "[" + get_current_time_as_string() + "] " + "[WARNING]" + log_string
        self._log_file_stream.write(log_message)
        self._log_file_stream.flush()

    def log_error(self, log_string: str):
        log_message = "[" + get_current_time_as_string() + "] " + "[ERROR]" + log_string
        self._log_file_stream.write(log_message)
        self._log_file_stream.flush()


class LogStreamEndReason(enum.Enum):
    LogFinished = 0
    LogError = 1
    ProgramError = 2


class ELogMessageType(enum.Enum):
    """
    Type of message to log
    """
    Log_PrimaryHeader = 0
    Log_SecondaryHeader = 1
    Log_General = 2
    Log_Warning = 3
    Log_Error = 4
    Log_Event = 5
    Log_NoFormat = 6


def add_log(log_stream, message: str, log_message_type: ELogMessageType = ELogMessageType.Log_General):
    message_prefix = ""
    date_string = "[" + get_current_time_as_string() + "] "
    message_postfix = ""

    if log_message_type != ELogMessageType.Log_NoFormat:
        message = message.strip()

    if log_message_type == ELogMessageType.Log_PrimaryHeader or log_message_type == ELogMessageType.Log_NoFormat:
        date_string = ""

    if log_message_type == ELogMessageType.Log_PrimaryHeader:
        message_prefix = "# "
        message_postfix = "  \n\n"
    elif log_message_type == ELogMessageType.Log_SecondaryHeader:
        message = "**" + message + "**"
        message_prefix = "\n## "
        message_postfix = "  \n"
    elif log_message_type == ELogMessageType.Log_General:
        message_postfix = "  \n"
    elif log_message_type == ELogMessageType.Log_Warning:
        message = "*" + message + "*"
        message_prefix = "> "
        message_postfix = "  \n"
    elif log_message_type == ELogMessageType.Log_Error:
        message = "**" + message + "**"
        message_prefix = "> "
        message_postfix = "  \n"
    elif log_message_type == ELogMessageType.Log_Event:
        message_prefix = "* "
        message_postfix = "  \n"

    message = message_prefix + date_string + message + message_postfix
    try:
        log_stream.write(message)
        log_stream.flush()
        return True
    except:
        # @todo remove bare 'except'
        return False


def close_log_file_stream(log_stream, reason=LogStreamEndReason):
    """
    Adds a final log message to logstream and closes it.
    """
    """
    If log stream is being closed because of a logging error, for example if the
    logstream is not open.
    """
    if reason == LogStreamEndReason.LogError:
        # We don't want the program to crash even if LogStream.close() throws an exception.
        # Because we are already aware that LogStream is being closed due to a LogError
        try:
            log_stream.close()
        except Exception as Ex:
            print(Ex)
            pass
        return

    message = ""
    if reason == LogStreamEndReason.LogFinished:
        message = "\n\nData logger completed logging task successfully. Log stream closed.\n\n"
    elif reason == LogStreamEndReason.ProgramError:
        message = "\n\nAn error was encountered amid logging task. Log stream closed.\n\n"

    add_log(log_stream, message, ELogMessageType.Log_NoFormat)

    # We want the program to crash if LogStream.close() throws an exception here. 
    log_stream.close()
    return
