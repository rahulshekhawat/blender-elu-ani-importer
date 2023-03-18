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


def handle_struct_unpack_error(err):
    message = "Struct Unpack Error"
    filelogger.add_log(globalvars.LogFileStream, message, filelogger.ELogMessageType.Log_Error)
    filelogger.close_log_file_stream(globalvars.LogFileStream, filelogger.LogStreamEndReason.ProgramError)
    exit()


def handle_assertion_error(err):
    Message = err.args[0]
    filelogger.add_log(globalvars.LogFileStream, Message, filelogger.ELogMessageType.Log_Error)
    filelogger.close_log_file_stream(globalvars.LogFileStream, filelogger.LogStreamEndReason.ProgramError)
    exit()
