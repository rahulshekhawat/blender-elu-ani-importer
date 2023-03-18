#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614

"""
This module contains global variables that will be used all across the project
"""

import os
import commonfunctions

INDEX_NONE: int = -1
STRING_NONE: str = ""

RAIDERZ_ASSETS_DIR: str = r'F:\Game Dev\asset_src'

LogFileName = commonfunctions.get_current_time_as_string()
# Replace all spaces and semicolons in FileName with hyphen
LogFileName = LogFileName.replace(' ', '-')
LogFileName = LogFileName.replace(':', '-')
# LogFileName += '.txt'
LogFileName += '.md'
LogFileName = os.getcwd() + os.sep + 'logs' + os.sep + LogFileName

LogFileStream = open(LogFileName, 'a+')
CurrentEluFileVersion = 0
CurrentAniFileVersion = 0
