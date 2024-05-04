#!/usr/bin/env python3

"""
This module contains the primary data type (FAniMesh) to load .ani files
"""

import aniparser
import raidflags
import globalvars
import binaryreader
import commonfunctions
from datatypes import FAniHeader
from datatypes import FAniNode
from datatypes import EAnimationType


class FAniMesh:

    def __init__(self, file_path: str):
        assert commonfunctions.is_valid_file_path(file_path), f"{file_path} is not a valid file path."
        assert commonfunctions.get_file_extension(file_path) == ".ani", f"{file_path} is not a .ani file type."
        self._source_file_path: str = file_path
        self._ani_header: FAniHeader = FAniHeader()
        self._ani_mesh_nodes = []
        self._ani_root_node = None
        self._loaded: bool = False

    def is_valid(self) -> bool:
        """
        Determines if this is a valid AniMesh object.
        :return: True if this AniMesh object contains a valid source file path
        """
        return commonfunctions.is_valid_file_path(self._source_file_path)

    def is_loaded(self) -> bool:
        """
        :return: True if the AniMesh data has been loaded into the memory from the source file.
        """
        return self._loaded

    def load_and_parse_ani_file(self) -> None:
        ani_file_stream = open(self._source_file_path, 'rb')
        self._ani_header.signature = binaryreader.read_unsigned_int(ani_file_stream, 1)[0]
        self._ani_header.version = binaryreader.read_unsigned_int(ani_file_stream, 1)[0]
        self._ani_header.max_frame = binaryreader.read_int(ani_file_stream, 1)[0]
        self._ani_header.model_num = binaryreader.read_int(ani_file_stream, 1)[0]
        self._ani_header.ani_type = EAnimationType(binaryreader.read_int(ani_file_stream, 1)[0])

        print(f"Currently parsing .ani file: {self._source_file_path}.\n Version: {self._ani_header.version}, maxframe: {self._ani_header.max_frame}, type: {self._ani_header.ani_type}")

        globalvars.CurrentAniFileVersion = self._ani_header.version

        if self._ani_header.version != raidflags.EXPORTER_CURRENT_ANI_VER:
            # @todo add warning - ani not latest version
            pass

        loader_obj = None
        if globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER12:
            loader_obj = aniparser.FAniFileLoaderImpl_v12()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER11:
            loader_obj = aniparser.FAniFileLoaderImpl_v11()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER9:
            loader_obj = aniparser.FAniFileLoaderImpl_v9()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER8:
            loader_obj = aniparser.FAniFileLoaderImpl_v7()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER7:
            loader_obj = aniparser.FAniFileLoaderImpl_v7()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER6:
            loader_obj = aniparser.FAniFileLoaderImpl_v6()
        else:
            # @todo ani version error
            pass

        for i in range(self._ani_header.model_num):
            ani_node = FAniNode()
            if self._ani_header.ani_type == EAnimationType.RAniType_Vertex:
                # if self.AniHeader.AniType == 1:
                loader_obj.LoadVertexAni(ani_node, ani_file_stream)
            elif self._ani_header.ani_type == EAnimationType.RAniType_Bone:
                # elif self.AniHeader.AniType == 2:
                loader_obj.LoadBoneAni(ani_node, ani_file_stream)
                if ani_node.Name == "Bip01":
                    self._ani_root_node = ani_node
            else:
                # @todo 
                pass
            loader_obj.LoadVisibilityKey(ani_node, ani_file_stream)
            self._ani_mesh_nodes.append(ani_node)

        self._loaded = True
        ani_file_stream.close()
