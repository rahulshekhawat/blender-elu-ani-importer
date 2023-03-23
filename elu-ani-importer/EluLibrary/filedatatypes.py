#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614
# pylint: disable=W0612


import os
import glob
import filelogger
import globalvars
import commonfunctions
import xml.etree.ElementTree as ETree


class FRaiderFilesManager:

    def __init__(self, source_dir: str = None, destination_dir: str = None) -> None:
        if source_dir is None:
            self.SourceDir = r'F:\Game Dev\asset_src'
        else:
            self.SourceDir = source_dir
        if destination_dir is None:
            self.DestinationDir = r'F:\Game Dev\asset_dest'
        else:
            self.DestinationDir = destination_dir

        # Source directories
        self.MonstersDirPath: str = self.SourceDir + r'\Model\Monster'
        self.StaticsDirPath: str = self.SourceDir + r'\Model\MapObject'
        self.FemaleDirPath: str = self.SourceDir + r'\Model\Player\hf'
        self.MaleDirPath: str = self.SourceDir + r'\Model\Player\hm'
        self.RidesDirPath: str = self.SourceDir + r'\Model\Ride'
        self.SkiesDirPath: str = self.SourceDir + r'\Model\Sky'
        self.WeaponsDirPath: str = self.SourceDir + r'\Model\weapons'
        self.NPCDirPath: str = self.SourceDir + r'\Model\NPC'
        self.SFXDirPath: str = self.SourceDir + r'\SFX'

        self.monsters_eluxml_files: list[str] = []
        self.mapobject_eluxml_files: list[str] = []
        self.female_eluxml_files: list[str] = []
        self.male_eluxml_files: list[str] = []
        self.rides_eluxml_files: list[str] = []
        self.skies_eluxml_files: list[str] = []
        self.weapons_eluxml_files: list[str] = []
        self.npc_eluxml_files: list[str] = []
        self.sfx_eluxml_files: list[str] = []

        self.fill_elu_xml_files_list()

    def fill_elu_xml_files_list(self):
        self.monsters_eluxml_files = commonfunctions.find_files(self.MonstersDirPath, '.elu.xml')
        self.mapobject_eluxml_files = commonfunctions.find_files(self.StaticsDirPath, '.elu.xml')
        self.female_eluxml_files = commonfunctions.find_files(self.FemaleDirPath, '.elu.xml')
        self.male_eluxml_files = commonfunctions.find_files(self.MaleDirPath, '.elu.xml')
        self.rides_eluxml_files = commonfunctions.find_files(self.RidesDirPath, '.elu.xml')
        self.skies_eluxml_files = commonfunctions.find_files(self.SkiesDirPath, '.elu.xml')
        self.weapons_eluxml_files = commonfunctions.find_files(self.WeaponsDirPath, '.elu.xml')
        self.npc_eluxml_files = commonfunctions.find_files(self.NPCDirPath, '.elu.xml')
        self.sfx_eluxml_files = commonfunctions.find_files(self.SFXDirPath, '.elu.xml')

    def raider_file_object_generator(self, eluxml_files):
        for eluxml_file in eluxml_files:
            raider_file_object = self.get_raider_file_object(eluxml_file)
            if raider_file_object is None:
                base_eluxml_name = os.path.basename(eluxml_file)
                message = "Couldn't find appropriate model and animation files related to - {0}".format(base_eluxml_name)
                filelogger.add_log(globalvars.LogFileStream, message, filelogger.ELogMessageType.Log_Error)
                continue
            else:
                yield raider_file_object

    def get_raider_file_object(self, eluxml_file):
        eluxml_dir = os.path.dirname(eluxml_file)
        file_name = os.path.basename(eluxml_file)
        elu_object_name = file_name.split('.')[0].strip()
        raider_files = glob.glob(eluxml_dir + "\\" + elu_object_name + ".*")

        # check if elu file exists
        elu_file_exists = False
        for raider_file in raider_files:
            raider_file_basename = os.path.basename(raider_file)
            raider_file_elements_list = raider_file_basename.split('.')
            if raider_file_elements_list[-1] == 'elu':
                elu_file_exists = True
                break

        # if elu file doesn't exist for current eluxml file, return None.
        if elu_file_exists is False:
            return None

        # else continue
        raider_file_object = FRaiderFileObject()
        raider_file_object.object_name = elu_object_name
        for raider_file in raider_files:
            raider_file_basename = os.path.basename(raider_file)
            raider_file_elements_list = raider_file_basename.split('.')
            if raider_file_elements_list[-1] == 'elu':
                raider_file_object.elu_file = raider_file
            if raider_file_elements_list[-2] == 'animation':
                raider_file_object.animation_xml_file = raider_file
            if raider_file_elements_list[-2] == 'animationevent':
                raider_file_object.animation_event_xml_file = raider_file
            if raider_file_elements_list[-2] == 'animationInfo':
                raider_file_object.animation_info_xml_file = raider_file
            if raider_file_elements_list[-2] == 'animationsoundevent':
                raider_file_object.animation_sound_event_xml_file = raider_file
            if raider_file_elements_list[-2] == 'elu':
                raider_file_object.elu_xml_file = raider_file
            if raider_file_elements_list[-2] == 'scene':
                raider_file_object.scene_xml_file = raider_file

        relative_object_dir = eluxml_dir.replace(self.SourceDir, "")
        raider_file_object.object_destination_folder = self.DestinationDir + relative_object_dir
        raider_file_object.object_model_folder = raider_file_object.object_destination_folder + os.sep + elu_object_name + os.sep + 'elu_model'
        raider_file_object.object_xml_folder = raider_file_object.object_destination_folder + os.sep + elu_object_name + os.sep + 'elu_xml_files'
        raider_file_object.object_ani_folder = raider_file_object.object_destination_folder + os.sep + elu_object_name + os.sep + 'elu_animations'
        if raider_file_object.animation_xml_file is not None:
            raider_file_object.ani_filenames = self.get_ani_filenames(raider_file_object.animation_xml_file)
        raider_file_object.materials_list = self.get_materials_list(eluxml_file)
        return raider_file_object

    @staticmethod
    def get_ani_filenames(animation_xml_file):
        animation_filenames = set()
        try:
            xml_tree = ETree.parse(animation_xml_file)
        except Exception:
            base_animation_xml_name = os.path.basename(animation_xml_file)
            message = "Couldn't parse {0}".format(base_animation_xml_name)
            filelogger.add_log(globalvars.LogFileStream, message, filelogger.ELogMessageType.Log_Warning)
            return animation_filenames

        xml_root = xml_tree.getroot()
        xml_ANIMATIONS = xml_root.findall("AddAnimation")
        for xml_ANIMATION in xml_ANIMATIONS:
            animation_filename = xml_ANIMATION.attrib["filename"]
            if animation_filename is not None:
                if animation_filename not in animation_filenames:
                    animation_filenames.add(animation_filename.lower())

        return animation_filenames

    @staticmethod
    def get_materials_list(eluxml_file):
        materials_list = []
        try:
            xml_tree = ETree.parse(eluxml_file)
        except Exception:
            base_eluxml_name = os.path.basename(eluxml_file)
            message = "Couldn't parse {0}".format(base_eluxml_name)
            filelogger.add_log(globalvars.LogFileStream, message, filelogger.ELogMessageType.Log_Warning)
            return materials_list

        xml_root = xml_tree.getroot()

        xml_MATERIALLISTs = xml_root.findall("MATERIALLIST")
        for xml_MATERIALLIST in xml_MATERIALLISTs:
            xml_MATERIALs = xml_MATERIALLIST.findall("MATERIAL")

            for xml_MATERIAL in xml_MATERIALs:
                material = xml_MATERIAL.attrib['name']
                materials_list.append(material)

        return materials_list


class FRaiderFileObject:

    def __init__(self) -> None:
        self.elu_file = None
        self.elu_xml_file = None
        self.animation_xml_file = None
        self.animation_event_xml_file = None
        self.animation_info_xml_file = None
        self.animation_sound_event_xml_file = None
        self.scene_xml_file = None
        self.object_name = None
        self.object_destination_folder = None
        self.object_model_folder = None
        self.object_xml_folder = None
        self.object_ani_folder = None
        self.ani_filenames = set()
        self.materials_list = []

    def has_animations(self) -> bool:
        if len(self.ani_filenames) > 0:
            return True
        else:
            return False
