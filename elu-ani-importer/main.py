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
__version__ = "1.1.0"
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
MODEL_FOLDER_TO_EXPORT = ERaiderZModelFolder.Monster  # This will export models only from inside 'monster' folder. See filedatatypes.py
EXPORT_TYPE = EExportType.SelectiveExport  # SelectiveExport will result in exporting only those models that contain SELECTIVE_EXPORT_KEYSTRING
SELECTIVE_EXPORT_KEYSTRING = "arek"

# SET SourceDir TO datadump/data FOLDER. DON'T LEAVE IT NONE
SourceDir = r"D:\DarkRaidAssets\asset_src"
# SET DestinationDir TO WHERE YOU WOULD LIKE TO EXPORT FBX FILES. DON'T LEAVE IT NONE
DestinationDir = r"D:\DarkRaidAssets\asset_dest_2"


def get_recordfile():
    LogDirectory = os.getcwd() + os.sep + "Logs"
    if os.path.exists(LogDirectory):
        assert os.path.isdir(LogDirectory)
    else:
        os.makedirs(LogDirectory)

    RecordFileStream = open(LogDirectory + os.sep + "RecordFile.txt", 'a+')
    return RecordFileStream


def process_static_or_skeletal_elumodel(RaiderFileObj, AniFilePaths):
    print("\nProcessing:", RaiderFileObj.elu_file)
    blenderfunctions.clear_blender()
    EluMeshObj = FEluMesh(RaiderFileObj.elu_file)
    blenderfunctions.draw_elu_skeleton(EluMeshObj)
    blender_materials = blenderfunctions.create_materials(RaiderFileObj.materials_list)
    blenderfunctions.draw_elu_mesh(EluMeshObj, blender_materials)
    blenderfunctions.export_mesh(RaiderFileObj, EluMeshObj)

    if RaiderFileObj.has_animations():
        animations = []
        for file_path in AniFilePaths:
            for filename in RaiderFileObj.ani_filenames:
                # Some files don't get detected because of lower/upper case issue. Hence using lower case for both
                if filename.lower() in file_path.lower():
                    # if filename.lower() in file_path.lower() and "die" in file_path.lower():
                    animations.append(file_path)
        blenderfunctions.load_and_export_animations(EluMeshObj, animations, RaiderFileObj)
    blenderfunctions.export_xml_files(RaiderFileObj)


def process_only_skeletal_elumodel(RaiderFileObj, AniFilePaths):
    print("\nProcessing:", RaiderFileObj.elu_file)
    blenderfunctions.clear_blender()
    EluMeshObj = FEluMesh(RaiderFileObj.elu_file)
    blenderfunctions.draw_elu_skeleton(EluMeshObj)
    blender_materials = blenderfunctions.create_materials(RaiderFileObj.materials_list)
    blenderfunctions.draw_elu_mesh(EluMeshObj, blender_materials)
    blenderfunctions.export_only_skeletal_meshes(RaiderFileObj, EluMeshObj)

    if RaiderFileObj.has_animations():
        animations = []
        for file_path in AniFilePaths:
            for filename in RaiderFileObj.ani_filenames:
                # Some files don't get detected because of lower/upper case issue. Hence using lower case for both
                if filename.lower() in file_path.lower():
                    # if filename.lower() in file_path.lower() and "die" in file_path.lower():
                    animations.append(file_path)
        blenderfunctions.load_and_export_animations(EluMeshObj, animations, RaiderFileObj)
    blenderfunctions.export_xml_files(RaiderFileObj)


def process_modular_skeletal_elumodel(RaiderFileObj, AniFilePaths):
    print("\nProcessing:", RaiderFileObj.elu_file)
    blenderfunctions.clear_blender()
    EluMeshObj = FEluMesh(RaiderFileObj.elu_file)
    blenderfunctions.draw_elu_skeleton(EluMeshObj)
    blender_materials = blenderfunctions.create_materials(RaiderFileObj.materials_list)
    blenderfunctions.draw_elu_mesh(EluMeshObj, blender_materials)
    blenderfunctions.export_modular_skeletal_meshses(RaiderFileObj, EluMeshObj)

    if RaiderFileObj.has_animations():
        animations = []
        for file_path in AniFilePaths:
            for filename in RaiderFileObj.ani_filenames:
                # Some files don't get detected because of lower/upper case issue. Hence using lower case for both
                if filename.lower() in file_path.lower():
                    # if filename.lower() in file_path.lower() and "die" in file_path.lower():
                    animations.append(file_path)
        blenderfunctions.load_and_export_animations(EluMeshObj, animations, RaiderFileObj)
    blenderfunctions.export_xml_files(RaiderFileObj)


def main(record_file_stream):
    record_file_list = record_file_stream.read().split('\n')

    raider_files_manager = filedatatypes.FRaiderFilesManager(SourceDir, DestinationDir)
    ani_file_paths = commonfunctions.find_files(raider_files_manager.SourceDir, ".ani")

    if EXPORT_TYPE == EExportType.MassExport:
        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.mapobject_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.weapons_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.skies_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.monsters_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.npc_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.sfx_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.female_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.male_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.rides_eluxml_files)

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            for RaiderObj in raider_obj_generator:
                if RaiderObj.elu_xml_file not in record_file_list:
                    process_static_or_skeletal_elumodel(RaiderObj, ani_file_paths)
                    record_file_list.append(RaiderObj.elu_xml_file)
                    record_file_stream.write(RaiderObj.elu_xml_file + "\n")
                    record_file_stream.flush()
                else:
                    continue

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            for RaiderObj in raider_obj_generator:
                if RaiderObj.elu_xml_file not in record_file_list:
                    process_only_skeletal_elumodel(RaiderObj, ani_file_paths)
                    record_file_list.append(RaiderObj.elu_xml_file)
                    record_file_stream.write(RaiderObj.elu_xml_file + "\n")
                    record_file_stream.flush()
                else:
                    continue

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            for RaiderObj in raider_obj_generator:
                if RaiderObj.elu_xml_file not in record_file_list:
                    if "hf_face_" in RaiderObj.elu_xml_file or "hm_face_" in RaiderObj.elu_xml_file:
                        process_only_skeletal_elumodel(RaiderObj, ani_file_paths)
                    else:
                        process_modular_skeletal_elumodel(RaiderObj, ani_file_paths)
                    record_file_list.append(RaiderObj.elu_xml_file)
                    record_file_stream.write(RaiderObj.elu_xml_file + "\n")
                    record_file_stream.flush()
                else:
                    continue

    elif EXPORT_TYPE == EExportType.SelectiveExport:
        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.mapobject_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.weapons_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.skies_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.monsters_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.npc_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.sfx_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.female_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.male_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            raider_obj_generator = raider_files_manager.raider_file_object_generator(raider_files_manager.rides_eluxml_files)

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            for RaiderObj in raider_obj_generator:
                if SELECTIVE_EXPORT_KEYSTRING in RaiderObj.elu_file:
                    process_static_or_skeletal_elumodel(RaiderObj, ani_file_paths)

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            for RaiderObj in raider_obj_generator:
                if SELECTIVE_EXPORT_KEYSTRING in RaiderObj.elu_file:
                    process_only_skeletal_elumodel(RaiderObj, ani_file_paths)

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male or \
                MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            for RaiderObj in raider_obj_generator:
                if SELECTIVE_EXPORT_KEYSTRING in RaiderObj.elu_file:
                    if "hf_face_" in RaiderObj.elu_xml_file or "hm_face_" in RaiderObj.elu_xml_file:
                        process_only_skeletal_elumodel(RaiderObj, ani_file_paths)
                    else:
                        process_modular_skeletal_elumodel(RaiderObj, ani_file_paths)
    print("Export finished!")


if __name__ == "__main__":
    RecordFileStream = get_recordfile()
    RecordFileStream.seek(0)
    main(RecordFileStream)
    RecordFileStream.flush()
    RecordFileStream.close()
