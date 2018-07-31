#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614

"""
Definitions for global variables
"""

import os
from . import commonfunctions

INDEX_NONE = -1
STRING_NONE = ""

RAIDERZ_ASSETS_DIR = r'F:\Game Dev\asset_src'

# LogFileName = commonfunctions.GetCurrentTimeAsString()
# Replace all spaces and semicolons in FileName with hyphen
# LogFileName = LogFileName.replace(' ', '-')
# LogFileName = LogFileName.replace(':', '-')
# LogFileName += '.txt'
# LogFileName += '.md'
# LogFileName = os.getcwd() + os.sep + 'logs' + os.sep + LogFileName
# LogFileStream = open(LogFileName, 'a+')

CurrentEluFileVersion = 0
CurrentAniFileVersion = 0
