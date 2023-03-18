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

from typing import Union


def get_current_time_as_string() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_valid_file_path(file_path: str) -> bool:
    return os.path.exists(file_path) and os.path.isfile(file_path)


def list_sub_dirs(dir_path: str) -> list[str]:
    """
    Returns a list of all subdirectories recursively in the given DirPath
    """
    dir_content = os.listdir(dir_path)

    # If there is no content (files or folders) inside DirPath, return empty list
    if not dir_content:
        return []

    # Subdirectories in current DirPath
    sub_dirs = [os.path.join(dir_path, sd) for sd in os.listdir(dir_path) if
                os.path.isdir(os.path.join(dir_path, sd))]

    # Directories inside subdirectory's subdirectory
    sub_dirs_sd = []
    for SubDir in sub_dirs:
        sub_dirs_sd += list_sub_dirs(SubDir)

    sub_dirs += sub_dirs_sd
    return sub_dirs


def find_files(dir_path: str, file_extension: str = "") -> list[str]:
    """
    Returns the list of all files inside the given directory (DirPath) and all
    of its subdirectories. If FileExtension is provided then only files
    with the given FileExtension are returned.\n
    File extension should be provided as .ext, not ext
    """
    files_list = []
    files_list += glob.glob(dir_path + '\\*' + file_extension)

    sub_dirs = list_sub_dirs(dir_path)
    for SubDir in sub_dirs:
        files_list += glob.glob(SubDir + '\\*' + file_extension)

    return files_list


def get_file_extension(file_path: str) -> Union[str, None]:
    """
    Returns file extension in .ext format, instead of ext.
    Returns None if FilePath is not a valid FilePath
    """
    if os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
        extension = file_name.split('.')[-1]
        extension = '.' + extension
        return extension
    else:
        return None


def get_file_name(file_path: str) -> Union[str, None]:
    """
    Returns file name from FilePath
    Returns None if FilePath is not a valid FilePath
    """
    if os.path.isfile(file_path):
        file_name = os.path.basename(file_path)
        return file_name
    else:
        return None
