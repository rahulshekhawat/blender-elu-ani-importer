#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614
# pylint: disable=W0612

"""
This module contains functions for loading and verifying ani files
"""

import math
import struct
import globalvars
import errorhandling
import datatypes
import binaryreader
import raidflags
import filelogger
from abc import ABC, abstractmethod


class FAniFileLoaderImpl(ABC):

    def __init__(self):
        super().__init__()
    
    @abstractmethod
    def LoadVertexAni(self, Node, FileStream, Offset=None):
        pass
    
    @abstractmethod
    def LoadBoneAni(self, Node, FileStream, Offset=None):
        pass

    @abstractmethod
    def LoadVisibilityKey(self, Node, FileStream, Offset=None):
        pass
    

class FAniFileLoaderImpl_v6(FAniFileLoaderImpl):

    def __init__(self):
        super().__init__()
    
    def LoadVertexAniBoundingBox(self, Node, FileStream):
        # @todo. Skipped for now because no data is read from FileStream
        pass
    
    def LoadVertexAni(self, Node, FileStream, Offset=None):
        try:
            Node.Name = binaryreader.read_word(FileStream)
            Node.VertexCount = binaryreader.read_int(FileStream, 1)[0]
            print("Vertex Count: ", Node.VertexCount)
            Node.Vertex_V_Count = binaryreader.read_int(FileStream, 1)[0]
            print("Vertex V Count: ", Node.Vertex_V_Count)
            # if Node.VertexCount > 0:
            for i in range(Node.VertexCount):
                VertFrame = binaryreader.read_unsigned_int(FileStream, 1)[0]
                Node.VertexFrame.append(VertFrame)
            
            for i in range(Node.VertexCount):
                Node.VertexTable.append([])
                for j in range(Node.Vertex_V_Count):
                    Vec = datatypes.FVector(binaryreader.read_float(FileStream, 3))
                    Node.VertexTable[i].append(Vec)

            self.LoadVertexAniBoundingBox(Node, FileStream)
        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)
    
    def LoadBoneAni(self, Node, FileStream, Offset=None):
        try:
            Node.Name = binaryreader.read_word(FileStream)
            if globalvars.CurrentAniFileVersion >= raidflags.EXPORTER_ANI_VER6:
                Node.ParentName = binaryreader.read_word(FileStream)

            Node.LocalMatrix = datatypes.FMatrix(binaryreader.read_float(FileStream, 16))

            PosKeyNum = binaryreader.read_int(FileStream, 1)[0]
            if PosKeyNum:
                Node.PositionKeyTrack.Count = PosKeyNum + 1
                for i in range(PosKeyNum):
                    PosKey = datatypes.FVecKey()
                    PosKey.Vector = datatypes.FVector(binaryreader.read_float(FileStream, 3))
                    PosKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    Node.PositionKeyTrack.Data.append(PosKey)
                LastPosKey = Node.PositionKeyTrack.Data[PosKeyNum - 1]
                Node.PositionKeyTrack.Data.append(LastPosKey)

            RotKeyNum = binaryreader.read_int(FileStream, 1)[0]
            if RotKeyNum:
                Node.RotationKeyTrack.Count = RotKeyNum + 1
                for i in range(RotKeyNum):
                    QuatKey = datatypes.FQuatKey()
                    QuatKey.Quat = datatypes.FQuaternion(binaryreader.read_float(FileStream, 4))
                    QuatKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    Node.RotationKeyTrack.Data.append(QuatKey)
                LastQuatKey = Node.RotationKeyTrack.Data[RotKeyNum - 1]
                Node.RotationKeyTrack.Data.append(LastQuatKey)

            if globalvars.CurrentAniFileVersion >= raidflags.EXPORTER_ANI_VER5:
                ScaleCount = binaryreader.read_int(FileStream, 1)[0]
                if ScaleCount:
                    Node.ScaleKeyTrack.Count = ScaleCount
                    for i in range(ScaleCount):
                        ScaleKey = datatypes.FVecKey()
                        ScaleKey.Vector = datatypes.FVector(binaryreader.read_float(FileStream, 3))
                        ScaleKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                        Node.ScaleKeyTrack.Data.append(ScaleKey)

        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)
        
    def LoadVisibilityKey(self, Node, FileStream, Offset=None):
        try:
            if globalvars.CurrentAniFileVersion >= raidflags.EXPORTER_ANI_VER5:
                VisCount = binaryreader.read_int(FileStream, 1)[0]
                Node.VisKeyTrack.Count = VisCount
                if VisCount:
                    for i in range(VisCount):
                        VisKey = datatypes.FVisKey()
                        VisKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                        VisKey.Vis = binaryreader.read_float(FileStream, 1)[0]
                        if VisKey.Vis < 0.0:
                            VisKey.Vis = 0.0
                        Node.VisKeyTrack.Data.append(VisKey)
                    return True
            else:
                VisCount = binaryreader.read_int(FileStream, 1)[0]
                Node.VisKeyTrack.Count = VisCount
                if VisCount:
                    for i in range(VisCount):
                        VisKey = datatypes.FVisKey()
                        VisKey.Vis = binaryreader.read_float(FileStream, 1)[0]
                        if VisKey.Vis < 0.0:
                            VisKey.Vis = 0.0
                        VisKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                        Node.VisKeyTrack.Data.append(VisKey)
                    return True            
            return False

        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)


class FAniFileLoaderImpl_v7(FAniFileLoaderImpl_v6):

    def __init__(self):
        super().__init__()
    
    def LoadVertexAniBoundingBox(self, Node, FileStream):
        try:
            Node.BoundingBox.vmin = datatypes.FVector(binaryreader.read_float(FileStream, 3))
            Node.BoundingBox.vmax = datatypes.FVector(binaryreader.read_float(FileStream, 3))
        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)


class FAniFileLoaderImpl_v9(FAniFileLoaderImpl_v7):

    def __init__(self):
        super().__init__()

    def LoadVisibilityKey(self, Node, FileStream, Offset=None):
        try:
            VisCount = binaryreader.read_int(FileStream, 1)[0]
            if VisCount:
                Node.VisKeyTrack.Count = VisCount
                for i in range(VisCount):
                    VisKey = datatypes.FVisKey()
                    VisKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    VisKey.Vis = binaryreader.read_float(FileStream, 1)[0]
                    Node.VisKeyTrack.Data.append(VisKey)
                return True
            return False

        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)


class FAniFileLoaderImpl_v11(FAniFileLoaderImpl_v9):

    def __init__(self):
        super().__init__()

    def LoadBoneAni(self, Node, FileStream, Offset=None):
        try:
            Node.Name = binaryreader.read_word(FileStream)
            Node.ParentName = binaryreader.read_word(FileStream)
            Node.LocalMatrix = datatypes.FMatrix(binaryreader.read_float(FileStream, 16))
            
            AnimType_1 = datatypes.FAnimType(binaryreader.read_int(FileStream, 3))
            if AnimType_1.Count > 0:
                Node.PositionKeyTrack.Count = AnimType_1.Count + 1
                for i in range(AnimType_1.Count):
                    PosKey = datatypes.FVecKey()
                    PosKey.Vector = datatypes.FVector(binaryreader.read_float(FileStream, 3))
                    PosKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    Node.PositionKeyTrack.Data.append(PosKey)
                LastPosKey = Node.PositionKeyTrack.Data[AnimType_1.Count - 1]
                Node.PositionKeyTrack.Data.append(LastPosKey)
            
            AnimType_2 = datatypes.FAnimType(binaryreader.read_int(FileStream, 3))
            if AnimType_2.Count > 0:
                Node.RotationKeyTrack.Count = AnimType_2.Count + 1
                for i in range(AnimType_2.Count):
                    QuatKey = datatypes.FQuatKey()
                    QuatKey.Quat = datatypes.FQuaternion(binaryreader.read_float(FileStream, 4))
                    QuatKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    Node.RotationKeyTrack.Data.append(QuatKey)
                LastQuatKey = Node.RotationKeyTrack.Data[AnimType_2.Count - 1]
                Node.RotationKeyTrack.Data.append(LastQuatKey)

            AnimType_3 = datatypes.FAnimType(binaryreader.read_int(FileStream, 3))
            if AnimType_3.Count > 0:
                Node.ScaleKeyTrack.Count = AnimType_3.Count
                for i in range(AnimType_3.Count):
                    ScaleKey = datatypes.FVecKey()
                    ScaleKey.Vector = datatypes.FVector(binaryreader.read_float(FileStream, 3))
                    ScaleKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    Node.ScaleKeyTrack.Data.append(ScaleKey)

        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)
        
    def LoadVisibilityKey(self, Node, FileStream, Offset=None):
        try:
            AnimType = datatypes.FAnimType(binaryreader.read_int(FileStream, 3))
            if AnimType.Count > 0:
                Node.VisKeyTrack.Count = AnimType.Count
                for i in range(AnimType.Count):
                    VisKey = datatypes.FVisKey()
                    VisKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    VisKey.Vis = binaryreader.read_float(FileStream, 1)[0]
                    Node.VisKeyTrack.Data.append(VisKey)

        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)


class FAniFileLoaderImpl_v12(FAniFileLoaderImpl_v11):

    def __init__(self):
        super().__init__()

    def LoadBoneAni(self, Node, FileStream, Offset=None):
        try:
            Node.Name = binaryreader.read_word(FileStream)
            
            Node.BaseTranslation = datatypes.FVector(binaryreader.read_float(FileStream, 3))
            Node.BaseRotation = datatypes.FQuaternion(binaryreader.read_float(FileStream, 4))
            Node.BaseScale = datatypes.FVector(binaryreader.read_int(FileStream, 3))

            AnimType_1 = datatypes.FAnimType(binaryreader.read_int(FileStream, 3))
            if AnimType_1.Count > 0:
                Node.PositionKeyTrack.Count = AnimType_1.Count + 1
                if AnimType_1.CountType == 10:
                    for i in range(AnimType_1.Count):
                        Frame = binaryreader.read_int(FileStream, 1)[0]
                        ShortTuple = binaryreader.read_unsigned_short(FileStream, 3)
                        FloatTuple = datatypes.convert_short_to_float(ShortTuple)
                        PosKey = datatypes.FVecKey()
                        PosKey.Frame = Frame
                        PosKey.Vector = datatypes.FVector(FloatTuple)
                        Node.PositionKeyTrack.Data.append(PosKey)
                    LastPosKey = Node.PositionKeyTrack.Data[AnimType_1.Count - 1]
                    Node.PositionKeyTrack.Data.append(LastPosKey)
                elif AnimType_1.CountType == 16:
                    for i in range(AnimType_1.Count):
                        PosKey = datatypes.FVecKey()
                        PosKey.Vector = datatypes.FVector(binaryreader.read_float(FileStream, 3))
                        PosKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                        Node.PositionKeyTrack.Data.append(PosKey)
                    LastPosKey = Node.PositionKeyTrack.Data[AnimType_1.Count - 1]
                    Node.PositionKeyTrack.Data.append(LastPosKey)
                else:
                    Message = "{0} node error: RAnimType_1.CountType is incorrect.".format(Node.Name)
                    filelogger.add_log(globalvars.LogFileStream, Message, filelogger.ELogMessageType.Log_Error)
                    return
            
            AnimType_2 = datatypes.FAnimType(binaryreader.read_int(FileStream, 3))
            if AnimType_2.Count > 0:
                Node.RotationKeyTrack.Count = AnimType_2.Count + 1
                if AnimType_2.CountType == 10:
                    for i in range(AnimType_2.Count):
                        Frame = binaryreader.read_int(FileStream, 1)[0]
                        ShortTuple = binaryreader.read_unsigned_short(FileStream, 3)
                        X, Y, Z = datatypes.convert_short_to_float(ShortTuple)
                        W = 0
                        FTol = X * X + Y * Y + Z * Z
                        if FTol <= 1.0:
                            Sub1 = 1.0 - FTol
                            FSqrt = math.sqrt(Sub1)
                            W = FSqrt
                        QuatKey = datatypes.FQuatKey()
                        QuatKey.Frame = Frame
                        QuatKey.Quat = datatypes.FQuaternion((X, Y, Z, W))
                        Node.RotationKeyTrack.Data.append(QuatKey)
                    LastQuatKey = Node.RotationKeyTrack.Data[AnimType_2.Count - 1]
                    Node.RotationKeyTrack.Data.append(LastQuatKey)
                elif AnimType_2.CountType == 16:
                    for i in range(AnimType_2.Count):
                        Frame = binaryreader.read_int(FileStream, 1)[0]
                        X, Y, Z = binaryreader.read_float(FileStream, 3)
                        W = 0
                        FTol = X * X + Y * Y + Z * Z
                        if FTol <= 1.0:
                            Sub1 = 1.0 - FTol
                            FSqrt = math.sqrt(Sub1)
                            W = FSqrt
                        QuatKey = datatypes.FQuatKey()
                        QuatKey.Frame = Frame
                        QuatKey.Quat = datatypes.FQuaternion((X, Y, Z, W))
                        Node.RotationKeyTrack.Data.append(QuatKey)
                    LastQuatKey = Node.RotationKeyTrack.Data[AnimType_2.Count - 1]
                    Node.RotationKeyTrack.Data.append(LastQuatKey)
                elif AnimType_2.CountType == 20:
                    for i in range(AnimType_2.Count):
                        QuatKey = datatypes.FQuatKey()
                        QuatKey.Quat = datatypes.FQuaternion(binaryreader.read_float(FileStream, 4))
                        QuatKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                        Node.RotationKeyTrack.Data.append(QuatKey)
                    LastQuatKey = Node.RotationKeyTrack.Data[AnimType_2.Count - 1]
                    Node.RotationKeyTrack.Data.append(LastQuatKey)
                else:
                    Message = "{0} node error: RAnimType_2.CountType is incorrect.".format(Node.Name)
                    filelogger.add_log(globalvars.LogFileStream, Message, filelogger.ELogMessageType.Log_Error)
                    return

            AnimType_3 = datatypes.FAnimType(binaryreader.read_int(FileStream, 3))
            if AnimType_3.Count > 0:
                Node.ScaleKeyTrack.Count = AnimType_3.Count
                for i in range(AnimType_3.Count):
                    ScaleKey = datatypes.FVecKey()
                    ScaleKey.Vector = datatypes.FVector(binaryreader.read_float(FileStream, 3))
                    ScaleKey.Frame = binaryreader.read_int(FileStream, 1)[0]
                    Node.ScaleKeyTrack.Data.append(ScaleKey)

        except struct.error as err:
            errorhandling.handle_struct_unpack_error(err)
