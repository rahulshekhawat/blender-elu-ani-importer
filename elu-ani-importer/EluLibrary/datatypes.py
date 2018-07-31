#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614
# pylint: disable=W0612

"""
"""

import os
import enum
import raidflags
import binaryreader
import globalvars
import struct


class FMatrix:

    def __init__(self, FloatTuple):
        self._00 = FloatTuple[0]
        self._01 = FloatTuple[1]
        self._02 = FloatTuple[2]
        self._03 = FloatTuple[3]
        self._10 = FloatTuple[4]
        self._11 = FloatTuple[5]
        self._12 = FloatTuple[6]
        self._13 = FloatTuple[7]
        self._20 = FloatTuple[8]
        self._21 = FloatTuple[9]
        self._22 = FloatTuple[10]
        self._23 = FloatTuple[11]
        self._30 = FloatTuple[12]
        self._31 = FloatTuple[13]
        self._32 = FloatTuple[14]
        self._33 = FloatTuple[15]

    def GetMatrixAsTuples(self):
        return ((self._00, self._01, self._02, self._03),
                (self._10, self._11, self._12, self._13),
                (self._20, self._21, self._22, self._23),
                (self._30, self._31, self._32, self._33))


class FVector:

    def __init__(self, FloatTuple):
        self.X = FloatTuple[0]
        self.Y = FloatTuple[1]
        self.Z = FloatTuple[2]

    def GetVecDataAsTuple(self):
        return (self.X, self.Y, self.Z)


class FVector4:

    def __init__(self, FloatTuple):
        self.X = FloatTuple[0]
        self.Y = FloatTuple[1]
        self.Z = FloatTuple[2]
        self.W = FloatTuple[3]

    @classmethod
    def FromVec3(cls, Vec3):
        return FVector4((Vec3.X, Vec3.Y, Vec3.Z, 1))


class FQuaternion:

    def __init__(self, FloatTuple):
        self.X = FloatTuple[0]
        self.Y = FloatTuple[1]
        self.Z = FloatTuple[2]
        self.W = FloatTuple[3]


class FBoundingBox:

    def __init__(self):
        self.vmin = None
        self.vmax = None

    def Add(self, Point):
        pass


class FFaceSubData:

    def __init__(self):
        self.p = 0
        self.uv = 0
        self.uv2 = 0
        self.n = 0
        self.n_tan = 0
        self.n_bin = 0


class FVertexIndex:

    def __init__(self):
        self.p = 0
        self.n = 0
        self.uv = 0
        self.uv2 = 0
        self.n_tan = 0
        self.n_bin = 0


class FVertexIndex_v12:

    def __init__(self):
        self.p = 0
        self.n = 0
        self.uv = 0
        self.n_tan = 0
        self.n_bin = 0


class FMeshPolygonData:

    def __init__(self):
        self.Vertices = 0
        self.MaterialID = 0
        self.FaceSubDatas = []


class FPhysiqueSubData:

    def __init__(self):
        self.cid = 0
        self.pid = 0
        self.weight = 0


class FPhysiqueInfo:

    def __init__(self):
        self.Num = 0
        self.PhysiqueSubDatas = []


class FMtrlTableInfo:

    def __init__(self):
        self.MaterialID = 0
        self.Offset = 0
        self.Count = 0
        self.SubMaterialIDForDrawMasking = 0


class RMeshAlign(enum.Enum):
    RMA_NONE = 0
    RMA_NORMAL = 1
    RMA_Z_FIXED = 2


class FEluNode:
    """
    This class contains all data related to an elu node.
    """

    def __init__(self):
        """
        Initialize all variables to default values
        """
        self.BipID = globalvars.INDEX_NONE

        self.NodeName = globalvars.STRING_NONE
        self.NodeParentName = globalvars.STRING_NONE
        self.ParentNodeID = globalvars.INDEX_NONE

        self.dwFlag = globalvars.INDEX_NONE
        self.MeshAlign = RMeshAlign.RMA_NONE
        self.BaseVisibility = 1.0  # Mesh should be visibile by default
        self.LODProjectIndex = 0  # LOD Index

        self.LocalMatrix = None
        self.BlenderMatrix = None
        self.BlenderLocalMatrix = None
        self.BlenderGlobalMatrix = None

        self.PointsCount = 0
        self.PointsTable = []

        self.NormalsCount = 0
        self.NormalsTable = []

        self.TangentTanCount = 0
        self.TangentTanTable = []

        self.TangentBinCount = 0
        self.TangentBinTable = []

        self.TexCoordCount = 0
        self.TexCoordTable = []

        self.TexCoordExtraCount = 0
        self.TexCoordExtraTable = []

        self.FaceCount = 0
        self.PolygonTable = []

        self.TotalDegrees = 0
        self.TotalTriangles = 0

        self.PointColorCount = 0
        self.PointColorTable = []

        self.MaterialID = globalvars.INDEX_NONE

        self.PhysiqueCount = 0
        self.PhysiqueTable = []

        self.BoneCount = 0
        self.BoneTable = []
        self.BoneTableIndices = []

        self.VertexIndexCount = 0
        self.VertexIndexTable = []

        self.FaceIndexCount = 0
        self.FaceIndexTable = []

        self.MaterialInfoCount = 0
        self.MaterialInfoTable = []

        self.BoundingBox = FBoundingBox()

    def CalculateLocalBoundingBox(self):
        for i in range(len(self.PointsTable)):
            self.BoundingBox.Add(self.PointsTable[i])

    def AddFlag(self, Flag):
        self.dwFlag |= Flag


class FEluHeader:

    def __init__(self):
        self.Signature = 0
        self.Version = 0
        self.MaterialNum = 0
        self.MeshNum = 0


class FAniHeader:

    def __init__(self):
        self.Signature = 0
        self.Version = 0
        self.MaxFrame = 0
        self.ModelNum = 0
        self.AniType = 0


class FVecKey:

    def __init__(self):
        self.Frame = 0
        self.Vector = None


class FQuatKey:

    def __init__(self):
        self.Frame = 0
        self.Quat = None


class FVisKey:

    def __init__(self):
        self.Frame = 0
        self.Vis = 0


class FAnimationTrack:

    def __init__(self):
        self.Count = 0
        self.Data = []


class FAnimType:

    def __init__(self, IntTuple):
        self.Type = IntTuple[0]
        self.CountType = IntTuple[1]
        self.Count = IntTuple[2]


class EAnimationType(enum.Enum):
    RAniType_TransForm = 0
    RAniType_Vertex = 1
    RAniType_Bone = 2
    RAniType_Tm = 3


class FAniNode:

    def __init__(self):
        self.Name = globalvars.STRING_NONE
        self.ParentName = globalvars.STRING_NONE
        self.VertexCount = 0  # Vertex Group (mesh-node) Count
        self.VertexTable = []

        self.Vertex_V_Count = 0  # Vertex Point Count
        self.VertexFrame = []

        self.LocalMatrix = None

        self.PositionKeyTrack = FAnimationTrack()
        self.RotationKeyTrack = FAnimationTrack()
        self.ScaleKeyTrack = FAnimationTrack()
        self.VisKeyTrack = FAnimationTrack()

        self.BoundingBox = FBoundingBox()

        self.BaseTranslation = None
        self.BaseRotation = None
        self.BaseScale = None


def HalfToFloatI_(Val):
    s = (Val >> 15) & 0x00000001
    e = (Val >> 10) & 0x0000001f
    m = Val & 0x000003ff

    if (e == 0):
        if (m == 0):
            return s << 31
        else:
            while (not (m & 0x00000400)):
                m <<= 1
                e -= 1
            e += 1
            m &= ~0x00000400

    elif (e == 31):
        if (m == 0):
            return s << 31 | 0x7f800000
        else:
            return s << 31 | 0x7f800000 | (m << 13)

    e = e + (127 - 15)
    m = m << 13

    return (s << 31) | (e << 23) | m


def HalfToFloat(Val):
    UIntVal = HalfToFloatI_(Val)
    data = struct.pack('<I', UIntVal)
    FloatVal = struct.unpack('<f', data)[0]
    return FloatVal


def ConvertShortToFloat(ShortTuple):
    X = HalfToFloat(ShortTuple[0])
    Y = HalfToFloat(ShortTuple[1])
    Z = HalfToFloat(ShortTuple[2])
    return (X, Y, Z)
