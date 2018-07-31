#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614
# pylint: disable=W0612

"""
"""

import os
import aniparser
import raidflags
import globalvars
import binaryreader
import commonfunctions
import errorhandling
from datatypes import FAniHeader
from datatypes import FAniNode
from datatypes import EAnimationType


class FAniMesh:

    def __init__(self, FilePath):
        self.AniHeader = FAniHeader()
        self.AniMeshNodes = []
        self.AniRootNode = None
        self.FilePath = FilePath
        self.SourceDir = os.path.dirname(FilePath)
        self.SourceFile = os.path.basename(FilePath)
        try:
            assert commonfunctions.GetFileExtension(self.FilePath) == '.ani', \
            "Assertion Failed: File extension is not .ani, FilePath: {0}".format(FilePath)
        except AssertionError as err:
            errorhandling.HandleAssertionError(err)
        self.AniFileStream = open(FilePath, 'rb')
        self.LoadAndParseAniFile()

    def LoadAndParseAniFile(self):
        self.AniHeader.Signature = binaryreader.ReadUInt(self.AniFileStream, 1)[0]
        self.AniHeader.Version = binaryreader.ReadUInt(self.AniFileStream, 1)[0]
        self.AniHeader.MaxFrame = binaryreader.ReadInt(self.AniFileStream, 1)[0]
        self.AniHeader.ModelNum = binaryreader.ReadInt(self.AniFileStream, 1)[0]
        # self.AniHeader.AniType = binaryreader.ReadInt(self.AniFileStream, 1)[0]
        self.AniHeader.AniType = EAnimationType(binaryreader.ReadInt(self.AniFileStream, 1)[0])

        print("Ani Version: {0}, ani maxframe: {1}, ani anitype: {2}".format(self.AniHeader.Version, self.AniHeader.MaxFrame, self.AniHeader.AniType))

        globalvars.CurrentAniFileVersion = self.AniHeader.Version

        if self.AniHeader.Version != raidflags.EXPORTER_CURRENT_ANI_VER:
            # @todo add warning - ani not latest version
            pass

        LoaderObj = None
        if globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER12:
            LoaderObj = aniparser.FAniFileLoaderImpl_v12()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER11:
            LoaderObj = aniparser.FAniFileLoaderImpl_v11()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER9:
            LoaderObj = aniparser.FAniFileLoaderImpl_v9()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER8:
            LoaderObj = aniparser.FAniFileLoaderImpl_v7()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER7:
            LoaderObj = aniparser.FAniFileLoaderImpl_v7()
        elif globalvars.CurrentAniFileVersion == raidflags.EXPORTER_ANI_VER6:
            LoaderObj = aniparser.FAniFileLoaderImpl_v6()
        else:
            # @todo ani version error
            pass

        for i in range(self.AniHeader.ModelNum):
            AniNode = FAniNode()
            if self.AniHeader.AniType == EAnimationType.RAniType_Vertex:
                # if self.AniHeader.AniType == 1:
                LoaderObj.LoadVertexAni(AniNode, self.AniFileStream)
            elif self.AniHeader.AniType == EAnimationType.RAniType_Bone:
                # elif self.AniHeader.AniType == 2:
                LoaderObj.LoadBoneAni(AniNode, self.AniFileStream)
                if AniNode.Name == "Bip01":
                    self.AniRootNode = AniNode
            else:
                # @todo 
                pass
            LoaderObj.LoadVisibilityKey(AniNode, self.AniFileStream)
            self.AniMeshNodes.append(AniNode)
        return
