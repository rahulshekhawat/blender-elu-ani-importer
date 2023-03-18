#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614
# pylint: disable=W0612

"""
"""

import os
import eluparser
import raidflags
import binaryreader
import errorhandling
import eluparser
import globalvars
import commonfunctions
from datatypes import FEluHeader
from datatypes import FEluNode


class FEluMesh:
    """
    Contains all the data read from a single Elu file
    """

    def __init__(self, file_path: str) -> None:
        self.EluHeader = FEluHeader()
        self.EluMeshNodes = []
        self.FilePath = file_path
        self.SourceDir = os.path.dirname(file_path)
        self.SourceFile = os.path.basename(file_path)
        try:
            commonfunctions.get_file_extension(self.FilePath) == '.elu' \
                                                                 "Assertion Failed: File extension is not .elu, " \
                                                                 "FilePath: {0}".format(
                file_path)
        except AssertionError as err:
            errorhandling.handle_assertion_error(err)
        self.EluFileStream = open(file_path, 'rb')
        self._load_and_parse_elu_file()

    def _load_and_parse_elu_file(self):
        self.EluHeader.Signature = binaryreader.read_unsigned_int(self.EluFileStream, 1)[0]
        self.EluHeader.Version = binaryreader.read_unsigned_int(self.EluFileStream, 1)[0]
        self.EluHeader.MaterialNum = binaryreader.read_int(self.EluFileStream, 1)[0]
        self.EluHeader.MeshNum = binaryreader.read_int(self.EluFileStream, 1)[0]
        globalvars.CurrentEluFileVersion = self.EluHeader.Version

        if self.EluHeader.Signature != raidflags.EXPORTER_SIG:
            # @todo add signature error
            pass

        if self.EluHeader.Version != raidflags.EXPORTER_CURRENT_MESH_VER:
            # @todo add warning -  elu not latest version
            pass

        loader_obj = None
        if globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER20:
            loader_obj = eluparser.FEluNodeLoaderImpl_v20()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER18:
            loader_obj = eluparser.FEluNodeLoaderImpl_v18()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER17:
            loader_obj = eluparser.FEluNodeLoaderImpl_v17()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER16:
            loader_obj = eluparser.FEluNodeLoaderImpl_v16()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER15:
            loader_obj = eluparser.FEluNodeLoaderImpl_v15()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER14:
            loader_obj = eluparser.FEluNodeLoaderImpl_v14()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER13:
            loader_obj = eluparser.FEluNodeLoaderImpl_v13()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER12:
            loader_obj = eluparser.FEluNodeLoaderImpl_v12()
        else:
            # @todo elu version error
            pass

        for i in range(self.EluHeader.MeshNum):
            elu_node = FEluNode()
            loader_obj.Load(elu_node, self.EluFileStream)
            self.EluMeshNodes.append(elu_node)
        return
