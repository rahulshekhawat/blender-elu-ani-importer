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
MODEL_FOLDER_TO_EXPORT = ERaiderZModelFolder.Monster    # This will export models only from inside 'monster' folder. See filedatatypes.py
EXPORT_TYPE = EExportType.SelectiveExport               # SelectiveExport will result in exporting only those models that contain SELECTIVE_EXPORT_KEYSTRING
SELECTIVE_EXPORT_KEYSTRING = "arek"    

def get_recordfile():
    LogDirectory = os.getcwd() + os.sep + "Logs"
    if os.path.exists(LogDirectory):
        assert os.path.isdir(LogDirectory)
    else:
        os.makedirs(LogDirectory)
    
    RecordFileStream = open(LogDirectory + os.sep +  "RecordFile.txt", 'a+')
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


def main(RecordFileStream):
    RecordFileList = RecordFileStream.read().split('\n')

    RaiderFilesManager = filedatatypes.FRaiderFilesManager()
    AniFilePaths = commonfunctions.FindFiles(RaiderFilesManager.SourceDir, ".ani")

    if EXPORT_TYPE == EExportType.MassExport:
        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.mapobject_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.weapons_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.skies_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.monsters_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.npc_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.sfx_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.female_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.male_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.rides_eluxml_files)

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            for RaiderObj in RaiderObjGenerator:
                if RaiderObj.elu_xml_file not in RecordFileList:
                    process_static_or_skeletal_elumodel(RaiderObj, AniFilePaths)
                    RecordFileList.append(RaiderObj.elu_xml_file)
                    RecordFileStream.write(RaiderObj.elu_xml_file + "\n")
                    RecordFileStream.flush()
                else:
                    continue

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            for RaiderObj in RaiderObjGenerator:
                if RaiderObj.elu_xml_file not in RecordFileList:
                    process_only_skeletal_elumodel(RaiderObj, AniFilePaths)
                    RecordFileList.append(RaiderObj.elu_xml_file)
                    RecordFileStream.write(RaiderObj.elu_xml_file + "\n")
                    RecordFileStream.flush()
                else:
                    continue

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            for RaiderObj in RaiderObjGenerator:
                if RaiderObj.elu_xml_file not in RecordFileList:
                    if "hf_face_" in RaiderObj.elu_xml_file or "hm_face_" in RaiderObj.elu_xml_file:
                        process_only_skeletal_elumodel(RaiderObj, AniFilePaths)
                    else:
                        process_modular_skeletal_elumodel(RaiderObj, AniFilePaths)
                    RecordFileList.append(RaiderObj.elu_xml_file)
                    RecordFileStream.write(RaiderObj.elu_xml_file + "\n")
                    RecordFileStream.flush()
                else:
                    continue

    elif EXPORT_TYPE == EExportType.SelectiveExport:
        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.mapobject_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.weapons_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.skies_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.monsters_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.npc_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.sfx_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.female_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.male_eluxml_files)
        elif MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            RaiderObjGenerator = RaiderFilesManager.RaiderFileObjectGenerator(RaiderFilesManager.rides_eluxml_files)
            
        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.MapObject or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Sky or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.SFX:
            for RaiderObj in RaiderObjGenerator:
                if SELECTIVE_EXPORT_KEYSTRING in RaiderObj.elu_file:
                    process_static_or_skeletal_elumodel(RaiderObj, AniFilePaths)

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Weapon or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.NPC or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Monster or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Ride:
            for RaiderObj in RaiderObjGenerator:
                if SELECTIVE_EXPORT_KEYSTRING in RaiderObj.elu_file:
                    process_only_skeletal_elumodel(RaiderObj, AniFilePaths)

        if MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Male or\
            MODEL_FOLDER_TO_EXPORT == ERaiderZModelFolder.Female:
            for RaiderObj in RaiderObjGenerator:
                if SELECTIVE_EXPORT_KEYSTRING in RaiderObj.elu_file:
                    if "hf_face_" in RaiderObj.elu_xml_file or "hm_face_" in RaiderObj.elu_xml_file:
                        process_only_skeletal_elumodel(RaiderObj, AniFilePaths)
                    else:
                        process_modular_skeletal_elumodel(RaiderObj, AniFilePaths)
    print("Export finished!")

if __name__ == "__main__":
    RecordFileStream = get_recordfile()
    RecordFileStream.seek(0)
    main(RecordFileStream)
    RecordFileStream.flush()
    RecordFileStream.close()
