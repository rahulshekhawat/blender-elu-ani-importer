#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703
# pylint: disable=W0614
# pylint: disable=W0612

"""
This module contains functions for loading and verifying elu files
"""

import struct
from . import raidflags
from . import datatypes
from . import binaryreader
from . import globalvars
# from abc import ABC, abstractmethod


class FEluNodeLoaderImpl():
    
    def __init__(self):
        # super().__init__()
        pass
    
    # @abstractmethod
    def Load(self, Node, FileStream, Offset=None):
        pass


class FEluNodeLoaderImpl_v12(FEluNodeLoaderImpl):
    """
    Version 12 of elu node loader
    """

    def __init__(self):
        super().__init__()

    def Load(self, Node, FileStream, Offset=None):
        """
        This function reads data from FileStream and writes it to Node\n
        @param Node EluNode that we need to write data to, from FileStream\n
        @param FileStream Binary data stream. // Constant\n
        @param Offset Cursor offset in FileStream\n
        @return Returns current offset of cursor\n
        """
        self.LoadName(Node, FileStream, Offset)
        self.LoadInfo(Node, FileStream, Offset)
        self.LoadVertex(Node, FileStream, Offset)
        self.LoadFace(Node, FileStream, Offset)
        self.LoadVertexInfo(Node, FileStream, Offset)
        self.LoadEtc(Node, FileStream, Offset)
        # @todo set BoundingBox
    
    def LoadName(self, Node, FileStream, Offset):
        try:
            Node.NodeName = binaryreader.ReadWord(FileStream)
            Node.NodeParentName = binaryreader.ReadWord(FileStream)
            Node.ParentNodeID = binaryreader.ReadInt(FileStream, 1)[0]
        except struct.error as err:
            pass

    def LoadInfo(self, Node, FileStream, Offset):
        try:
            Node.dwFlag = binaryreader.ReadUInt(FileStream, 1)[0]
            try:
                Node.MeshAlign = datatypes.RMeshAlign(binaryreader.ReadInt(FileStream, 1)[0])
            except ValueError as er:
                pass
            
            if globalvars.CurrentEluFileVersion < raidflags.EXPORTER_MESH_VER11:
                # Unused data
                AniPartsType = binaryreader.ReadInt(FileStream, 1)[0]
                PartsPosInfoType = binaryreader.ReadInt(FileStream, 1)[0]
                PartsType = binaryreader.ReadInt(FileStream, 1)[0]
            
            Node.LocalMatrix = datatypes.FMatrix(binaryreader.ReadFloat(FileStream, 16))
            if globalvars.CurrentEluFileVersion >= raidflags.EXPORTER_MESH_VER11:
                Node.BaseVisibility = binaryreader.ReadInt(FileStream, 1)[0]

        except struct.error as err:
            pass

    def LoadVertex(self, Node, FileStream, Offset):
        try:
            Node.PointsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointsTable.append(Vec)
            
            if Node.PointsCount:
                Node.CalculateLocalBoundingBox()
            
            Node.NormalsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.NormalsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.NormalsTable.append(Vec)
            
            Node.TangentTanCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentTanCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Vec4 = datatypes.FVector4.FromVec3(Vec)
                Node.TangentTanTable.append(Vec4)
                
            Node.TangentBinCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentBinCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TangentBinTable.append(Vec)
                
            Node.TexCoordCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordTable.append(Vec)
        except struct.error as err:
            pass

    def LoadFace(self, Node, FileStream, Offset):
        try:
            Node.FaceCount = binaryreader.ReadInt(FileStream, 1)[0]
            if(Node.FaceCount):
                if globalvars.CurrentEluFileVersion < raidflags.EXPORTER_MESH_VER12:
                    for i in range(Node.FaceCount):
                        MeshPolygonData = datatypes.FMeshPolygonData()
                        MeshPolygonData.Vertices = 3
                        for j in range(j):
                            UnsignedShorts = binaryreader.ReadUShort(FileStream, 5)
                            FaceSubData = datatypes.FFaceSubData()
                            FaceSubData.p = UnsignedShorts[0]
                            FaceSubData.uv = UnsignedShorts[1]
                            FaceSubData.n = UnsignedShorts[2]
                            FaceSubData.uv2 = -1
                            FaceSubData.n_tan = UnsignedShorts[3]
                            FaceSubData.n_bin = UnsignedShorts[4]
                            MeshPolygonData.FaceSubDatas.append(FaceSubData)
                        MeshPolygonData.MaterialID = binaryreader.ReadShort(FileStream, 1)[0]
                        Node.PolygonTable.append(MeshPolygonData)
                    Node.TotalDegrees = Node.FaceCount * 3
                    Node.TotalTriangles = Node.FaceCount
                else:
                    Node.TotalDegrees = binaryreader.ReadInt(FileStream, 1)[0]
                    Node.TotalTriangles = binaryreader.ReadInt(FileStream, 1)[0]
                    for i in range(Node.FaceCount):
                        MeshPolygonData = datatypes.FMeshPolygonData()
                        MeshPolygonData.Vertices = binaryreader.ReadInt(FileStream, 1)[0]
                        for j in range(MeshPolygonData.Vertices):
                            UnsignedShorts = binaryreader.ReadUShort(FileStream, 5)
                            FaceSubData = datatypes.FFaceSubData()
                            FaceSubData.p = UnsignedShorts[0]
                            FaceSubData.uv = UnsignedShorts[1]
                            FaceSubData.n = UnsignedShorts[2]
                            FaceSubData.uv2 = -1
                            FaceSubData.n_tan = UnsignedShorts[3]
                            FaceSubData.n_bin = UnsignedShorts[4]
                            MeshPolygonData.FaceSubDatas.append(FaceSubData)
                        MeshPolygonData.MaterialID = binaryreader.ReadShort(FileStream, 1)[0]
                        Node.PolygonTable.append(MeshPolygonData)
                    try:
                        assert Node.TotalDegrees == sum(len(MeshPolygonData.FaceSubDatas) \
                        for MeshPolygonData in Node.PolygonTable), \
                        "Assertion Failed: TotalDegrees value does not match expected value for node - {}".format(Node.NodeName)
                    except AssertionError as err:
                        pass
        except struct.error as err:
            pass

    def LoadVertexInfo(self, Node, FileStream, Offset):
        try:
            Node.PointColorCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointColorCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointColorTable.append(Vec)
            
            if Node.PointsCount == 0 or Node.FaceCount == 0:
                Node.AddFlag(raidflags.RM_FLAG_DUMMY_MESH)
            
            Node.MaterialID = binaryreader.ReadInt(FileStream, 1)[0]
            Node.PhysiqueCount = binaryreader.ReadInt(FileStream, 1)[0]

            if Node.PhysiqueCount:
                try:
                    assert Node.PointsCount == Node.PhysiqueCount, \
                    "Assertion Failed: Points Count is not same as Physique Count - {0}".format(Node.NodeName)
                except AssertionError as err:
                    pass
                for i in range(Node.PhysiqueCount):
                    Size = binaryreader.ReadInt(FileStream, 1)[0]
                    PhysiqueInfo = datatypes.FPhysiqueInfo()
                    for j in range (Size):
                        PhysiqueSubData = datatypes.FPhysiqueSubData()
                        PhysiqueSubData.cid = binaryreader.ReadUShort(FileStream, 1)[0]
                        PhysiqueSubData.pid = binaryreader.ReadUShort(FileStream, 1)[0]
                        PhysiqueSubData.weight = binaryreader.ReadFloat(FileStream, 1)[0]
                        PhysiqueInfo.PhysiqueSubDatas.append(PhysiqueSubData)
                    PhysiqueInfo.Num = len(PhysiqueInfo.PhysiqueSubDatas)
                    Node.PhysiqueTable.append(PhysiqueInfo)

                    if Size > raidflags.PHYSIQUE_MAX_WEIGHT:
                        for m in range(Size):
                            for n in range(m + 1, Size):
                                if PhysiqueInfo.PhysiqueSubDatas[m].weight < PhysiqueInfo.PhysiqueSubDatas[n].weight:
                                    Temp = datatypes.FPhysiqueSubData()
                                    Temp = PhysiqueInfo.PhysiqueSubDatas[m]
                                    PhysiqueInfo.PhysiqueSubDatas[m] = PhysiqueInfo.PhysiqueSubDatas[n]
                                    PhysiqueInfo.PhysiqueSubDatas[n] = Temp

                        fSum3 = sum(PhysiqueSubData.weight for PhysiqueSubData in PhysiqueInfo.PhysiqueSubDatas)
                        PhysiqueInfo.PhysiqueSubDatas[0].weight = PhysiqueInfo.PhysiqueSubDatas[0].weight / fSum3
                        PhysiqueInfo.PhysiqueSubDatas[1].weight = PhysiqueInfo.PhysiqueSubDatas[1].weight / fSum3
                        PhysiqueInfo.PhysiqueSubDatas[2].weight = PhysiqueInfo.PhysiqueSubDatas[2].weight / fSum3
                        PhysiqueInfo.Num = 3
                    
        except struct.error as err:
            pass
    
    def LoadEtc(self, Node, FileStream, Offset):
        try:
            Node.BoneCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.BoneCount):
                Matrix = datatypes.FMatrix(binaryreader.ReadFloat(FileStream, 16))
                Node.BoneTable.append(Matrix)
            
            for i in range(Node.BoneCount):
                BoneIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                Node.BoneTableIndices.append(BoneIndex)
            
            Node.VertexIndexCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.VertexIndexCount):
                VertexIndex = datatypes.FVertexIndex()
                UnsignedShorts = binaryreader.ReadUShort(FileStream, 5)
                VertexIndex.p = UnsignedShorts[0]
                VertexIndex.n = UnsignedShorts[1]
                VertexIndex.uv = UnsignedShorts[2]
                VertexIndex.uv2 = -1
                VertexIndex.n_tan = UnsignedShorts[3]
                VertexIndex.n_bin = UnsignedShorts[4]

            if globalvars.CurrentEluFileVersion < raidflags.EXPORTER_MESH_VER12:
                for i in range(Node.FaceCount):
                    for j in range(3):
                        FaceIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                        Node.FaceIndexTable.append(FaceIndex)  
                Node.FaceIndexCount = Node.FaceCount * 3                  
            else:
                PrimitiveType = binaryreader.ReadInt(FileStream, 1)[0]
                Node.FaceIndexCount = binaryreader.ReadInt(FileStream, 1)[0]
                for i in range(Node.FaceIndexCount):
                    FaceIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                    Node.FaceIndexTable.append(FaceIndex)

            Node.MaterialInfoCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.MaterialInfoCount):
                MtrlTableInfo = datatypes.FMtrlTableInfo()
                if globalvars.CurrentEluFileVersion < raidflags.EXPORTER_MESH_VER9:
                    MtrlTableInfo.MaterialID = binaryreader.ReadInt(FileStream, 1)[0]
                    MtrlTableInfo.Offset = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.Count = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.SubMaterialIDForDrawMasking = binaryreader.ReadInt(FileStream, 1)[0]
                else:
                    MtrlTableInfo.MaterialID = binaryreader.ReadInt(FileStream, 1)[0]
                    MtrlTableInfo.Offset = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.Count = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.SubMaterialIDForDrawMasking = binaryreader.ReadInt(FileStream, 1)[0]
                Node.MaterialInfoTable.append(MtrlTableInfo)
            
            # @todo GetBipID

        except struct.error as err:
            pass


class FEluNodeLoaderImpl_v13(FEluNodeLoaderImpl_v12):

    def __init__(self):
        super().__init__()
    
    def Load(self, Node, FileStream, Offset=None):
        self.LoadName(Node, FileStream, Offset)
        self.LoadInfo(Node, FileStream, Offset)
        self.LoadVertex(Node, FileStream, Offset)
        self.LoadFace(Node, FileStream, Offset)
        self.LoadVertexInfo(Node, FileStream, Offset)
        self.LoadEtc(Node, FileStream, Offset)
    
    def LoadEtc(self, Node, FileStream, Offset):
        super().LoadEtc(Node, FileStream, Offset)
        try:
            Node.BoundingBox.vmin = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
            Node.BoundingBox.vmax = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))        
        except struct.error as err:
            pass


class FEluNodeLoaderImpl_v14(FEluNodeLoaderImpl_v13):
    
    def __init__(self):
        super().__init__()
    
    def LoadVertex(self, Node, FileStream, Offset):
        try:
            dwFVF = binaryreader.ReadUInt(FileStream, 1)[0]

            Node.PointsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointsTable.append(Vec)
                
            if Node.PointsCount:
                Node.CalculateLocalBoundingBox()
            
            Node.NormalsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.NormalsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.NormalsTable.append(Vec)
            
            Node.TangentTanCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentTanCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Vec4 = datatypes.FVector4.FromVec3(Vec)
                Node.TangentTanTable.append(Vec4)
                
            Node.TangentBinCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentBinCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TangentBinTable.append(Vec)
                
            Node.TexCoordCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordTable.append(Vec)
                        
        except struct.error as err:
            pass


class FEluNodeLoaderImpl_v15(FEluNodeLoaderImpl_v14):
    
    def __init__(self):
        super().__init__()
    
    def LoadFace(self, Node, FileStream, Offset):
        try:
            Node.FaceCount = binaryreader.ReadInt(FileStream, 1)[0]
            if(Node.FaceCount):
                Node.TotalDegrees = binaryreader.ReadInt(FileStream, 1)[0]
                Node.TotalTriangles = binaryreader.ReadInt(FileStream, 1)[0]
                for i in range(Node.FaceCount):
                    MeshPolygonData = datatypes.FMeshPolygonData()
                    MeshPolygonData.Vertices = binaryreader.ReadInt(FileStream, 1)[0]
                    for j in range(MeshPolygonData.Vertices):
                        UnsignedShorts = binaryreader.ReadUShort(FileStream, 6)
                        FaceSubData = datatypes.FFaceSubData()
                        FaceSubData.p = UnsignedShorts[0]
                        FaceSubData.uv = UnsignedShorts[1]
                        FaceSubData.uv2 = UnsignedShorts[2]
                        FaceSubData.n = UnsignedShorts[3]
                        FaceSubData.n_tan = UnsignedShorts[4]
                        FaceSubData.n_bin = UnsignedShorts[5]
                        MeshPolygonData.FaceSubDatas.append(FaceSubData)
                    MeshPolygonData.MaterialID = binaryreader.ReadShort(FileStream, 1)[0]
                    Node.PolygonTable.append(MeshPolygonData)
                try:
                    assert Node.TotalDegrees == sum(len(MeshPolygonData.FaceSubDatas) \
                    for MeshPolygonData in Node.PolygonTable), \
                    "Assertion Failed: TotalDegrees value does not match expected value for node - {}".format(Node.NodeName)
                except AssertionError as err:
                    pass
                    
        except struct.error as err:
            pass

    def LoadVertex(self, Node, FileStream, Offset):
        try:
            dwFVF = binaryreader.ReadUInt(FileStream, 1)[0]
            LightMapID = binaryreader.ReadInt(FileStream, 1)[0]

            Node.PointsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointsTable.append(Vec)
            
            if Node.PointsCount:
                Node.CalculateLocalBoundingBox()

            Node.NormalsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.NormalsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.NormalsTable.append(Vec)
            
            Node.TangentTanCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentTanCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Vec4 = datatypes.FVector4.FromVec3(Vec)
                Node.TangentTanTable.append(Vec4)
                
            Node.TangentBinCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentBinCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TangentBinTable.append(Vec)
                
            Node.TexCoordCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordTable.append(Vec)

            LightMapTexCoordTableCount = binaryreader.ReadInt(FileStream, 1)[0]
            FileStream.seek(FileStream.tell() + 3 * 4 * LightMapTexCoordTableCount)
        except struct.error as err:
            pass

    def LoadEtc(self, Node, FileStream, Offset):
        try:
            Node.BoneCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.BoneCount):
                Matrix = datatypes.FMatrix(binaryreader.ReadFloat(FileStream, 16))
                Node.BoneTable.append(Matrix)
            
            for i in range(Node.BoneCount):
                BoneIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                Node.BoneTableIndices.append(BoneIndex)
            
            Node.VertexIndexCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.VertexIndexCount):
                VertexIndex = datatypes.FVertexIndex()
                UnsignedShorts = binaryreader.ReadUShort(FileStream, 6)
                VertexIndex.p = UnsignedShorts[0]
                VertexIndex.n = UnsignedShorts[1]
                VertexIndex.uv = UnsignedShorts[2]
                VertexIndex.uv2 = UnsignedShorts[3]
                VertexIndex.n_tan = UnsignedShorts[4]
                VertexIndex.n_bin = UnsignedShorts[5]
                Node.VertexIndexTable.append(VertexIndex)

            if globalvars.CurrentEluFileVersion < raidflags.EXPORTER_MESH_VER12:
                for i in range(Node.FaceCount):
                    for j in range(3):
                        FaceIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                        Node.FaceIndexTable.append(FaceIndex)  
                Node.FaceIndexCount = Node.FaceCount * 3                  
            else:
                PrimitiveType = binaryreader.ReadInt(FileStream, 1)[0]
                Node.FaceIndexCount = binaryreader.ReadInt(FileStream, 1)[0]
                for i in range(Node.FaceIndexCount):
                    FaceIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                    Node.FaceIndexTable.append(FaceIndex)

            Node.MaterialInfoCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.MaterialInfoCount):
                MtrlTableInfo = datatypes.FMtrlTableInfo()
                if globalvars.CurrentEluFileVersion < raidflags.EXPORTER_MESH_VER9:
                    MtrlTableInfo.MaterialID = binaryreader.ReadInt(FileStream, 1)[0]
                    MtrlTableInfo.Offset = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.Count = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.SubMaterialIDForDrawMasking = binaryreader.ReadInt(FileStream, 1)[0]
                else:
                    MtrlTableInfo.MaterialID = binaryreader.ReadInt(FileStream, 1)[0]
                    MtrlTableInfo.Offset = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.Count = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.SubMaterialIDForDrawMasking = binaryreader.ReadInt(FileStream, 1)[0]
                Node.MaterialInfoTable.append(MtrlTableInfo)
            
            # @todo GetBipID
            Node.BoundingBox.vmin = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
            Node.BoundingBox.vmax = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))  

        except struct.error as err:
            pass


class FEluNodeLoaderImpl_v16(FEluNodeLoaderImpl_v15):
    
    def __init__(self):
        super().__init__()
  
    def LoadVertex(self, Node, FileStream, Offset):
        try:
            dwFVF = binaryreader.ReadUInt(FileStream, 1)[0]
            LightMapID = binaryreader.ReadInt(FileStream, 1)[0]

            Node.PointsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointsTable.append(Vec)
                
            if Node.PointsCount:
                Node.CalculateLocalBoundingBox()
            
            Node.NormalsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.NormalsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.NormalsTable.append(Vec)
            
            Node.TangentTanCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentTanCount):
                Vec = datatypes.FVector4(binaryreader.ReadFloat(FileStream, 4))
                Node.TangentTanTable.append(Vec)
                
            Node.TangentBinCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentBinCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TangentBinTable.append(Vec)
                
            Node.TexCoordCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordTable.append(Vec)

            LightMapTexCoordTableCount = binaryreader.ReadInt(FileStream, 1)[0]
            FileStream.seek(FileStream.tell() + 3 * 4 * LightMapTexCoordTableCount)
        except struct.error as err:
            pass


class FEluNodeLoaderImpl_v17(FEluNodeLoaderImpl_v16):
    
    def __init__(self):
        super().__init__()
        
    def LoadVertex(self, Node, FileStream, Offset):
        try:
            dwFVF = binaryreader.ReadUInt(FileStream, 1)[0]
            LightMapID = binaryreader.ReadInt(FileStream, 1)[0]

            Node.PointsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointsTable.append(Vec)
                
            if Node.PointsCount:
                Node.CalculateLocalBoundingBox()
            
            Node.NormalsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.NormalsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.NormalsTable.append(Vec)
            
            Node.TangentTanCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentTanCount):
                Vec = datatypes.FVector4(binaryreader.ReadFloat(FileStream, 4))
                Node.TangentTanTable.append(Vec)
                
            Node.TangentBinCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentBinCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TangentBinTable.append(Vec)
                
            Node.TexCoordCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordTable.append(Vec)

        except struct.error as err:
            pass


class FEluNodeLoaderImpl_v18(FEluNodeLoaderImpl_v17):
    
    def __init__(self):
        super().__init__()

    def LoadVertex(self, Node, FileStream, Offset):
        try:
            Node.PointsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointsTable.append(Vec)
                
            if Node.PointsCount:
                Node.CalculateLocalBoundingBox()
            
            Node.NormalsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.NormalsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.NormalsTable.append(Vec)
            
            Node.TangentTanCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentTanCount):
                Vec = datatypes.FVector4(binaryreader.ReadFloat(FileStream, 4))
                Node.TangentTanTable.append(Vec)
                
            Node.TangentBinCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentBinCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TangentBinTable.append(Vec)
                
            Node.TexCoordCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordTable.append(Vec)

            Node.TexCoordExtraCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordExtraCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordExtraTable.append(Vec)

        except struct.error as err:
            pass


class FEluNodeLoaderImpl_v20(FEluNodeLoaderImpl_v18):
    
    def __init__(self):
        super().__init__()
        
    def LoadName(self, Node, FileStream, Offset):
        try:
            Node.NodeName = binaryreader.ReadWord(FileStream)
            Node.ParentNodeID = binaryreader.ReadInt(FileStream, 1)[0]
            Node.NodeParentName = binaryreader.ReadWord(FileStream)
        except struct.error as err:
            pass
    
    def LoadInfo(self, Node, FileStream, Offset):
        try:
            Node.LocalMatrix = datatypes.FMatrix(binaryreader.ReadFloat(FileStream, 16))

            Node.BaseVisibility = binaryreader.ReadFloat(FileStream, 1)[0]
            Node.dwFlag = binaryreader.ReadUInt(FileStream, 1)[0]
            try:
                Node.MeshAlign = datatypes.RMeshAlign(binaryreader.ReadInt(FileStream, 1)[0])
            except ValueError as er:
                pass
            Node.LODProjectIndex = binaryreader.ReadInt(FileStream, 1)[0]

        except struct.error as err:
            pass

    def LoadVertex(self, Node, FileStream, Offset):
        try:
            Node.PointsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.PointsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.PointsTable.append(Vec)
                
            if Node.PointsCount:
                Node.CalculateLocalBoundingBox()
                
            Node.TexCoordCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordTable.append(Vec)

            Node.TexCoordExtraCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TexCoordExtraCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TexCoordExtraTable.append(Vec)
            
            Node.NormalsCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.NormalsCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.NormalsTable.append(Vec)
            
            Node.TangentTanCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentTanCount):
                Vec = datatypes.FVector4(binaryreader.ReadFloat(FileStream, 4))
                Node.TangentTanTable.append(Vec)
                
            Node.TangentBinCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.TangentBinCount):
                Vec = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
                Node.TangentBinTable.append(Vec)

        except struct.error as err:
            pass

    def LoadEtc(self, Node, FileStream, Offset):
        try:
            PrimitiveType = binaryreader.ReadInt(FileStream, 1)[0]

            Node.VertexIndexCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.VertexIndexCount):
                VertexIndex = datatypes.FVertexIndex()
                UnsignedShorts = binaryreader.ReadUShort(FileStream, 6)
                VertexIndex.p = UnsignedShorts[0]
                VertexIndex.n = UnsignedShorts[1]
                VertexIndex.uv = UnsignedShorts[2]
                VertexIndex.uv2 = UnsignedShorts[3]
                VertexIndex.n_tan = UnsignedShorts[4]
                VertexIndex.n_bin = UnsignedShorts[5]
                Node.VertexIndexTable.append(VertexIndex)

            Node.BoneCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.BoneCount):
                Matrix = datatypes.FMatrix(binaryreader.ReadFloat(FileStream, 16))
                Node.BoneTable.append(Matrix)
            
            for i in range(Node.BoneCount):
                BoneIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                Node.BoneTableIndices.append(BoneIndex)

            Node.MaterialInfoCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.MaterialInfoCount):
                MtrlTableInfo = datatypes.FMtrlTableInfo()
                if globalvars.CurrentEluFileVersion < raidflags.EXPORTER_MESH_VER9:
                    MtrlTableInfo.MaterialID = binaryreader.ReadInt(FileStream, 1)[0]
                    MtrlTableInfo.Offset = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.Count = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.SubMaterialIDForDrawMasking = binaryreader.ReadInt(FileStream, 1)[0]
                else:
                    MtrlTableInfo.MaterialID = binaryreader.ReadInt(FileStream, 1)[0]
                    MtrlTableInfo.Offset = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.Count = binaryreader.ReadUShort(FileStream, 1)[0]
                    MtrlTableInfo.SubMaterialIDForDrawMasking = binaryreader.ReadInt(FileStream, 1)[0]
                Node.MaterialInfoTable.append(MtrlTableInfo)
            
            Node.FaceIndexCount = binaryreader.ReadInt(FileStream, 1)[0]
            for i in range(Node.FaceIndexCount):
                FaceIndex = binaryreader.ReadUShort(FileStream, 1)[0]
                Node.FaceIndexTable.append(FaceIndex)
            
            # @todo GetBipID
            Node.BoundingBox.vmin = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))
            Node.BoundingBox.vmax = datatypes.FVector(binaryreader.ReadFloat(FileStream, 3))  

            # @todo fix bounding box
        except struct.error as err:
            pass
