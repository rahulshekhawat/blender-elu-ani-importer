#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703

"""
* elu files loader and exporter for blender
* Run this script from inside blender.
"""

__author__ = "Ryujin Ishima"
__copyright__ = ""
__credits__ = "[Ryujin Ishima]"
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Ryujin Ishima"
__email__ = "ryujin.hawk@gmail.com"
__status__ = "Production"

import os
main_file_path = os.path.dirname(os.path.realpath(__file__))
sub_folder = "Blender" + os.sep + "BlenderEluLoader.blend"
main_folder = main_file_path.replace(sub_folder, "")

import sys
sys.path.append(main_folder + "EluLibrary")

import enum
import globalvars
import filedatatypes
import commonfunctions
import blenderfunctions
from elumesh import FEluMesh


class ERaiderZModelFolder(enum.Enum):
    Monster = 0
    NPC = 1
    Female = 2
    Male = 3
    MapObject = 4
    Ride = 5
    Sky = 6
    Weapon = 7
    SFX = 8

class EExportType(enum.Enum):
    MassExport = 0
    SelectiveExport = 1

# SET FOLLOWING BEFORE IMPORT/EXPORT
MODEL_FOLDER_TO_EXPORT = ERaiderZModelFolder.Male   # This will export models only from inside 'hm' folder. See filedatatypes.py
EXPORT_TYPE = EExportType.SelectiveExport           # SelectiveExport will result in exporting only those models that contain SELECTIVE_EXPORT_KEYSTRING
SELECTIVE_EXPORT_KEYSTRING = "face"    

def get_recordfile():
    LogDirectory = os.getcwd() + os.sep + "Logs"
    if os.path.exists(LogDirectory):
        assert os.path.isdir(LogDirectory)
    else:
        os.makedirs(LogDirectory)
    
    RecordFileStream = open(LogDirectory + os.sep +  "RecordFile.txt", 'a+')
    return RecordFileStream
