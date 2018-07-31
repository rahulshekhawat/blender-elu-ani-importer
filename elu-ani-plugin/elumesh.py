#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614
# pylint: disable=W0612

"""
"""

import os
from . import eluparser
from . import raidflags
from . import binaryreader
from . import eluparser
from . import globalvars
from . import commonfunctions
from . import datatypes


class FEluMesh:
    """
    Contains all the data read from a single Elu file
    """

    def __init__(self, FilePath):
        self.EluHeader = datatypes.FEluHeader()
        self.EluMeshNodes = []
        self.FilePath = FilePath
        self.SourceDir = os.path.dirname(FilePath)
        self.SourceFile = os.path.basename(FilePath)
        try:
            commonfunctions.GetFileExtension(self.FilePath) == '.elu'\
            "Assertion Failed: File extension is not .elu, FilePath: {0}".format(FilePath)
        except AssertionError as err:
            pass
        self.EluFileStream = open(FilePath, 'rb')
        self.LoadAndParseEluFile()


    def LoadAndParseEluFile(self):
        self.EluHeader.Signature =  binaryreader.ReadUInt(self.EluFileStream, 1)[0]
        self.EluHeader.Version = binaryreader.ReadUInt(self.EluFileStream, 1)[0]
        self.EluHeader.MaterialNum = binaryreader.ReadInt(self.EluFileStream, 1)[0]
        self.EluHeader.MeshNum = binaryreader.ReadInt(self.EluFileStream, 1)[0]
        globalvars.CurrentEluFileVersion = self.EluHeader.Version

        if self.EluHeader.Signature != raidflags.EXPORTER_SIG:
            # @todo add signature error
            pass
        
        if self.EluHeader.Version != raidflags.EXPORTER_CURRENT_MESH_VER:
            # @todo add warning -  elu not latest version
            pass
        
        LoaderObj = None
        if globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER20:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v20()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER18:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v18()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER17:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v17()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER16:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v16()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER15:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v15()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER14:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v14()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER13:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v13()
        elif globalvars.CurrentEluFileVersion == raidflags.EXPORTER_MESH_VER12:
            LoaderObj = eluparser.FEluNodeLoaderImpl_v12()
        else:
            # @todo elu version error
            pass
                    
        for i in range(self.EluHeader.MeshNum):
            EluNode = datatypes.FEluNode()
            LoaderObj.Load(EluNode, self.EluFileStream)
            self.EluMeshNodes.append(EluNode)
        return
            