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

from typing import TypeVar

FVector4Type = TypeVar("FVector4Type", bound="FVector4")


class FMatrix:

    def __init__(self, float_tuple: tuple) -> None:
        self._00: float = float_tuple[0]
        self._01: float = float_tuple[1]
        self._02: float = float_tuple[2]
        self._03: float = float_tuple[3]
        self._10: float = float_tuple[4]
        self._11: float = float_tuple[5]
        self._12: float = float_tuple[6]
        self._13: float = float_tuple[7]
        self._20: float = float_tuple[8]
        self._21: float = float_tuple[9]
        self._22: float = float_tuple[10]
        self._23: float = float_tuple[11]
        self._30: float = float_tuple[12]
        self._31: float = float_tuple[13]
        self._32: float = float_tuple[14]
        self._33: float = float_tuple[15]

    def get_matrix_as_tuples(self) -> tuple[tuple[float, ...], ...]:
        return ((self._00, self._01, self._02, self._03),
                (self._10, self._11, self._12, self._13),
                (self._20, self._21, self._22, self._23),
                (self._30, self._31, self._32, self._33))


class FVector:

    def __init__(self, float_tuple: tuple[float, ...]) -> None:
        self.X: float = float_tuple[0]
        self.Y: float = float_tuple[1]
        self.Z: float = float_tuple[2]

    def get_vec_data_as_tuple(self) -> tuple[float, ...]:
        return self.X, self.Y, self.Z


class FVector4:

    def __init__(self, float_tuple: tuple[float, ...]) -> None:
        self.X: float = float_tuple[0]
        self.Y: float = float_tuple[1]
        self.Z: float = float_tuple[2]
        self.W: float = float_tuple[3]

    @classmethod
    def from_vec3(cls, vec3: FVector) -> FVector4Type:
        return FVector4((vec3.X, vec3.Y, vec3.Z, 1))


class FQuaternion:

    def __init__(self, float_tuple: tuple[float, ...]) -> None:
        self.X: float = float_tuple[0]
        self.Y: float = float_tuple[1]
        self.Z: float = float_tuple[2]
        self.W: float = float_tuple[3]


class FBoundingBox:

    def __init__(self):
        self.vmin = None
        self.vmax = None

    def add(self, point):
        # @todo
        pass


class FFaceSubData:

    def __init__(self) -> None:
        self.p: int = 0
        self.uv: int = 0
        self.uv2: int = 0
        self.n: int = 0
        self.n_tan: int = 0
        self.n_bin: int = 0


class FVertexIndex:

    def __init__(self) -> None:
        self.p: int = 0
        self.n: int = 0
        self.uv: int = 0
        self.uv2: int = 0
        self.n_tan: int = 0
        self.n_bin: int = 0


class FvertexindexV12:

    def __init__(self):
        self.p: int = 0
        self.n: int = 0
        self.uv: int = 0
        self.n_tan: int = 0
        self.n_bin: int = 0


class FMeshPolygonData:

    def __init__(self):
        self.Vertices: int = 0
        self.MaterialID: int = 0
        self.FaceSubDatas: list[FFaceSubData] = []


class FPhysiqueSubData:

    def __init__(self):
        self.cid: int = 0
        self.pid: int = 0
        self.weight: float = 0.0


class FPhysiqueInfo:

    def __init__(self):
        self.Num: int = 0
        self.PhysiqueSubDatas: list[FPhysiqueSubData] = []


class FMtrlTableInfo:

    def __init__(self):
        self.MaterialID: int = 0
        self.Offset: int = 0
        self.Count: int = 0
        self.SubMaterialIDForDrawMasking: int = 0


class RMeshAlign(enum.Enum):
    RMA_NONE = 0
    RMA_NORMAL = 1
    RMA_Z_FIXED = 2


class FEluNode:
    """
    This class contains all data related to an elu node.
    """

    def __init__(self) -> None:
        """
        Initialize all variables to default values
        """
        self.BipID: int = globalvars.INDEX_NONE

        self.NodeName: str = globalvars.STRING_NONE
        self.NodeParentName: str = globalvars.STRING_NONE
        self.ParentNodeID: int = globalvars.INDEX_NONE

        self.dwFlag: int = globalvars.INDEX_NONE
        self.MeshAlign: RMeshAlign = RMeshAlign.RMA_NONE
        self.BaseVisibility: float = 1.0  # Mesh should be visible by default
        self.LODProjectIndex: int = 0  # LOD Index

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

    def calculate_local_bounding_box(self) -> None:
        for i in range(len(self.PointsTable)):
            self.BoundingBox.add(self.PointsTable[i])

    def add_flag(self, flag) -> None:
        self.dwFlag |= flag


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

    def __init__(self, int_tuple: tuple[int, ...]):
        self.Type: int = int_tuple[0]
        self.CountType: int = int_tuple[1]
        self.Count: int = int_tuple[2]


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


def half_to_float_i_(val):
    s = (val >> 15) & 0x00000001
    e = (val >> 10) & 0x0000001f
    m = val & 0x000003ff

    if e == 0:
        if m == 0:
            return s << 31
        else:
            while not (m & 0x00000400):
                m <<= 1
                e -= 1
            e += 1
            m &= ~0x00000400

    elif e == 31:
        if m == 0:
            return s << 31 | 0x7f800000
        else:
            return s << 31 | 0x7f800000 | (m << 13)

    e = e + (127 - 15)
    m = m << 13

    return (s << 31) | (e << 23) | m


def half_to_float(val: int) -> float:
    u_int_val = half_to_float_i_(val)
    data = struct.pack('<I', u_int_val)
    float_val = struct.unpack('<f', data)[0]
    return float_val


def convert_short_to_float(short_tuple) -> tuple[float, ...]:
    x = half_to_float(short_tuple[0])
    y = half_to_float(short_tuple[1])
    z = half_to_float(short_tuple[2])
    return x, y, z
