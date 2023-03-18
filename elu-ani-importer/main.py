#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703

"""
* elu files loader and exporter for blender
* Run this script from inside blender.
"""

__author__ = "Rahul Shekhawat"
__copyright__ = ""
__credits__ = "[Rahul Shekhawat]"
__license__ = ""
__version__ = "1.0.0"
__maintainer__ = "Rahul Shekhawat"
__email__ = "rahul.shekhawat.dev.mail@gmail.com"
__status__ = "Release"

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


elu_file_path = r"G:\RaiderZDev\RaiderzAssets\WildRaiderzAssets\datadump\Data\Model\Monster\basteroe\basteroe.elu"
ani_file_path = r"G:\RaiderZDev\RaiderzAssets\WildRaiderzAssets\datadump\Data\Model\Monster\basteroe\basteroe_atk_1.elu.ani"


def load_elu_skeleton(skeleton_path):
    blenderfunctions.clear_blender()
    elu_mesh_obj = FEluMesh(elu_file_path)
    blenderfunctions.draw_elu_skeleton(elu_mesh_obj)
    # blender_materials = blenderfunctions.create_materials()
    blenderfunctions.draw_elu_mesh(elu_mesh_obj, [])
    animations = [ani_file_path]

    raiderz_file_obj = None
    blenderfunctions.load_and_export_animations(elu_mesh_obj, animations, raiderz_file_obj)


load_elu_skeleton(elu_file_path)


"""
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
# Following will export models only from inside 'monster' folder. See filedatatypes.py
MODEL_FOLDER_TO_EXPORT = ERaiderZModelFolder.Monster
# SelectiveExport will result in exporting only those models that contain SELECTIVE_EXPORT_KEYSTRING
EXPORT_TYPE = EExportType.SelectiveExport
SELECTIVE_EXPORT_KEYSTRING = "basteroe"

# SET SourceDir TO datadump/data FOLDER. DON'T LEAVE IT NONE
SourceDir = r'G:\RaiderZDev\RaiderzAssets\WildRaiderzAssets\datadump\Data'
# SET DestinationDir TO WHERE YOU WOULD LIKE TO EXPORT FBX FILES. DON'T LEAVE IT NONE
DestinationDir = r'G:\RaiderZDev\RaiderzAssets\ConvertedAssets'


def get_record_file():
    log_directory = os.getcwd() + os.sep + "Logs"
    if os.path.exists(log_directory):
        assert os.path.isdir(log_directory)
    else:
        os.makedirs(log_directory)
    record_file_stream = open(log_directory + os.sep + "recordfile.txt", 'a+')
    return record_file_stream


def main(in_record_file):
    record_file_list = record_file.read().split('\n')
    raiderz_files_manager = filedatatypes.FRaiderFilesManager(SourceDir, DestinationDir)
    animation_files_paths = commonfunctions.find_files(raiderz_files_manager.SourceDir, ".ani")

    # if EXPORT_TYPE == EExportType.MassExport:

if __name__ == "__main__":
    record_file = get_record_file()
    record_file.seek(0)
    main(record_file)
    record_file.flush()
    record_file.close()
"""
