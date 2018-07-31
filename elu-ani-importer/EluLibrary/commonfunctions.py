#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614

"""
This module contains global methods
"""

import datetime
import os
import glob


def GetCurrentTimeAsString():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def IsValidFilePath(FilePath):
    """
    @todo - function not implemented yet
    Returns true if FilePath is a valid-
    """
    # @todo Finish code
    return None


def ListSubdirs(DirPath):
    """
    Returns a list of all subdirectories recursively in the given DirPath
    """
    DirContent = os.listdir(DirPath)

    # If there is no content (files or folders) inside DirPath, return empty list
    if not DirContent:
        return []
    
    # Sub directories in current DirPath
    SubDirs = [os.path.join(DirPath, sd) for sd in os.listdir(DirPath) if
               os.path.isdir(os.path.join(DirPath, sd))]

    # Directories inside subdirectory's subdirectory
    SubDirs_SD = []
    for SubDir in SubDirs:
        SubDirs_SD += ListSubdirs(SubDir)
    
    SubDirs += SubDirs_SD
    return SubDirs


def FindFiles(DirPath, FileExtension=""):
    """
    Returns the list of all files inside the given directory (DirPath) and all
    of it's sub-directories. If FileExtension is provided then only files 
    with the given FileExtension are returned.\n
    File extension should be provided as .ext, not ext
    """
    FilesList = []
    FilesList += glob.glob(DirPath + '\\*' + FileExtension)

    SubDirs = ListSubdirs(DirPath)
    for SubDir in SubDirs:
        FilesList += glob.glob(SubDir + '\\*' + FileExtension)
    
    return FilesList


def GetFileExtension(FilePath):
    """
    Returns file extension in .ext format, instead of ext.
    Returns None if FilePath is not a valid FilePath
    """
    if os.path.isfile(FilePath):
        FileName = os.path.basename(FilePath)
        Extension = FileName.split('.')[-1]
        Extension = '.' + Extension
        return Extension
    else:
        return None


def GetFileName(FilePath):
    """
    Returns file name from FilePath
    Returns None if FilePath is not a valid FilePath
    """
    if os.path.isfile(FilePath):
        FileName = os.path.basename(FilePath)
        return FileName
    else:
        return None
