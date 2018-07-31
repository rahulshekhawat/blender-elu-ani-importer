#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614

"""
This module contains functionality to add and save logs to files
"""

import os
import shutil
import enum
from commonfunctions import GetCurrentTimeAsString


class LogStreamEndReason(enum.Enum):
    LogFinished = 0
    LogError = 1
    ProgramError = 2


class LogType(enum.Enum):
    """
    Deprecated. Don't use it.
    """
    LogType_None = 0
    LogType_General = 1
    LogType_Warning = 2
    LogType_Error = 3
    LogType_Meta = 4


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


def AddLog(LogStream, Message, LogMessageType=ELogMessageType.Log_General):
    MessagePrefix = ""
    DateString = "[" + GetCurrentTimeAsString() + "] "
    MessagePostfix = ""

    if LogMessageType != ELogMessageType.Log_NoFormat:
        Message = Message.strip()

    if LogMessageType == ELogMessageType.Log_PrimaryHeader or LogMessageType == ELogMessageType.Log_NoFormat:
        DateString = ""

    if LogMessageType == ELogMessageType.Log_PrimaryHeader:
        MessagePrefix = "# "
        MessagePostfix = "  \n\n"
    elif LogMessageType == ELogMessageType.Log_SecondaryHeader:
        Message = "**" + Message + "**"
        MessagePrefix = "\n## "
        MessagePostfix = "  \n"
    elif LogMessageType == ELogMessageType.Log_General:
        MessagePostfix = "  \n"
    elif LogMessageType == ELogMessageType.Log_Warning:
        Message = "*" + Message + "*"
        MessagePrefix = "> "
        MessagePostfix = "  \n"
    elif LogMessageType == ELogMessageType.Log_Error:
        Message = "**" + Message + "**"
        MessagePrefix = "> "
        MessagePostfix = "  \n"
    elif LogMessageType == ELogMessageType.Log_Event:
        MessagePrefix = "* "
        MessagePostfix = "  \n"
    
    Message = MessagePrefix + DateString + Message + MessagePostfix
    try:
        LogStream.write(Message)
        LogStream.flush()
        return True
    except:
        return False


def CloseLogFileStream(LogStream, Reason=LogStreamEndReason):
    """
    Adds a final log message to logstream and closes it.
    """
    """
    If log stream is being closed because of a logging error, for example if the
    logstream is not open.
    """
    if Reason == LogStreamEndReason.LogError:
        # We don't want the program to crash even if LogStream.close() throws an exception.
        # Because we are already aware that LogStream is being closed due to a LogError
        try:
            LogStream.close()
        except Exception as Ex:
            print(Ex)
            pass
        return

    Message = ""
    if Reason == LogStreamEndReason.LogFinished:
        Message = "\n\nData logger completed logging task successfully. Log stream closed.\n\n"
    elif Reason == LogStreamEndReason.ProgramError:
        Message = "\n\nAn error was encountered amid logging task. Log stream closed.\n\n"

    AddLog(LogStream, Message, ELogMessageType.Log_NoFormat)

    # We want the program to crash if LogStream.close() throws an exception here. 
    LogStream.close()
    return


def AddLog_Deprecated(FileStream, Message, Logtype=LogType.LogType_General):
    """
    Returns true if message was added successfully to LogFile
    """
    # Add time stamp to message
    
    if Logtype == LogType.LogType_None:
        pass
    elif Logtype == LogType.LogType_General:
        Message = "general - " + Message
    elif Logtype == LogType.LogType_Warning:
        Message = "warning - " + Message
    elif Logtype == LogType.LogType_Error:
        Message = "error - " + Message
    else:
        pass

    if Logtype != LogType.LogType_Meta:
        Message = '[' + GetCurrentTimeAsString() + ']: ' + Message + '\n'
    else:
        pass

    try:
        FileStream.write(Message)
        FileStream.flush()
        return True
    except:
        return False


def CloseLogFileStream_Deprecated(LogStream, Reason=LogStreamEndReason.LogFinished):
    """
    Adds a final log message to logstream and closes it.
    """
    """
    If log stream is being closed because of a logging error, for example if the
    logstream is not open.
    """
    if Reason == LogStreamEndReason.LogError:
        # We don't want the program to crash even if LogStream.close() throws an exception.
        # Because we are already aware that LogStream is being closed due to a LogError
        try:
            LogStream.close()
        except Exception as Ex:
            print(Ex)
            pass
        return

    if Reason == LogStreamEndReason.LogFinished:
        Message = "Data logger completed logging task successfully. Log stream closed.\n\n\n"
    elif Reason == LogStreamEndReason.ProgramError:
        Message = "An error was encountered amid logging task. Log stream closed.\n\n\n"

    AddLog(LogStream, Message)

    # We want the program to crash if LogStream.close() throws an exception here. 
    LogStream.close()
    return
