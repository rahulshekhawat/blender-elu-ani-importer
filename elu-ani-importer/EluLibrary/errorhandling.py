#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614

"""
This module contains methods to properly handle errors and close the program
"""

import filelogger
import globalvars


def HandleStructUnpackError(err):
    Message = "Struct Unpack Error"
    filelogger.AddLog(globalvars.LogFileStream, Message, filelogger.ELogMessageType.Log_Error)
    filelogger.CloseLogFileStream(globalvars.LogFileStream, filelogger.LogStreamEndReason.ProgramError)
    exit()


def HandleAssertionError(err):
    Message = err.args[0]
    filelogger.AddLog(globalvars.LogFileStream, Message, filelogger.ELogMessageType.Log_Error)
    filelogger.CloseLogFileStream(globalvars.LogFileStream, filelogger.LogStreamEndReason.ProgramError)
    exit()
