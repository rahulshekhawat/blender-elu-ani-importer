#!/usr/bin/env python3
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=W0703

"""
Helper functions to process .elu and .ani files in blender
"""

try:
    import bpy
    import bmesh
    from mathutils import *
except ImportError:
    print("Please run the script from inside blender")
    exit()

import os
import shutil
import datatypes
import globalvars
from elumesh import FEluMesh
from animesh import FAniMesh


def reset_blender():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def clear_blender():
    for action in bpy.data.actions:
        bpy.data.actions.remove(action, do_unlink=True)

    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh, True)

    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature, True)

    for material in bpy.data.materials:
        bpy.data.materials.remove(material, True)

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj)

    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, True)


def reload_blender():
    bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)


def draw_elu_skeleton(elu_mesh_obj):
    armature = bpy.data.armatures.new("root_armature")
    armature_obj = bpy.data.objects.new("armature_obj", armature)

    current_scene = bpy.context.scene
    current_scene.objects.link(armature_obj)
    current_scene.objects.active = armature_obj

    armature_obj.select = True
    armature.draw_type = "STICK"
    armature_obj.show_x_ray = True
    armature.show_names = True

    current_scene.update()

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="EDIT")
    else:
        print("mode_set() context is incorrect. Current mode is: {0}".format(bpy.context.mode))
        return

    for EluMeshNode in elu_mesh_obj.EluMeshNodes:
        EluMeshNode.BlenderLocalMatrix = Matrix(EluMeshNode.LocalMatrix.GetMatrixAsTuples())
        EluMeshNode.BlenderLocalMatrix.transpose()

        # Default BlenderGlobalMatrix is same BlenderLocalMatrix
        EluMeshNode.BlenderGlobalMatrix = EluMeshNode.BlenderLocalMatrix

    bone_names_list = []
    for EluMeshNode in elu_mesh_obj.EluMeshNodes:
        bone_name = EluMeshNode.NodeName
        bone_names_list.append(bone_name)
        edit_bone = armature.edit_bones.new(bone_name)
        edit_bone.tail = edit_bone.head + Vector((0.0, 0.0, 0.5))
        parent_name = EluMeshNode.NodeParentName
        parent_id = EluMeshNode.ParentNodeID
        if parent_id >= 0 and parent_name != globalvars.STRING_NONE:
            parent_edit_bone = armature.edit_bones[parent_name]
            edit_bone.parent = parent_edit_bone

    for edit_bone in armature.edit_bones:
        if edit_bone.parent is None:
            for EluMeshNode in elu_mesh_obj.EluMeshNodes:
                if edit_bone.name == EluMeshNode.NodeName:
                    edit_bone.matrix = EluMeshNode.BlenderLocalMatrix
        else:
            for EluMeshNode in elu_mesh_obj.EluMeshNodes:
                if edit_bone.name == EluMeshNode.NodeName:
                    EluMeshNode.BlenderGlobalMatrix = edit_bone.parent.matrix * EluMeshNode.BlenderLocalMatrix
                    edit_bone.matrix = EluMeshNode.BlenderGlobalMatrix

    bpy.ops.object.mode_set(mode="OBJECT")


def create_materials(materials_list):
    blender_materials = []
    for material_name in materials_list:
        blender_mat = bpy.data.materials.new(material_name)
        blender_materials.append(blender_mat)
    return blender_materials


def draw_elu_mesh(elu_mesh_obj, blender_materials):
    # Skeleton
    armature_object = None
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            armature_object = obj

    for EluNode in elu_mesh_obj.EluMeshNodes:

        # if elu node is not a mesh, skip
        if EluNode.PointsCount <= 0:
            continue

        # Skip drawing col_oo and hide_oo meshes
        if "col_oo" in EluNode.NodeName or "hide_oo" in EluNode.NodeName or "hide" in EluNode.NodeName:
            continue
        
        if EluNode.NodeName.startswith("Box00"):
            continue

        if EluNode.NodeName.endswith("col"):
            continue

        if "Box" in EluNode.NodeName:
            pass

        # Used this line in extracting Catacomb_of_damned_East_1_tomb meshes properly
        # if "Object010" in EluNode.NodeName:
        #     continue

        # Test if there is a bone map for our current elu mesh
        mesh_name = EluNode.NodeName + '-mesh'
        mesh = bpy.data.meshes.new(mesh_name)
        mesh_obj = bpy.data.objects.new(mesh_name, mesh)

        scene = bpy.context.scene
        scene.objects.link(mesh_obj)

        faces = []
        for Polygon in EluNode.PolygonTable:
            face = []
            for FaceSubData in Polygon.FaceSubDatas:
                face.append(FaceSubData.p)
            faces.append(face)

        points = []
        for NodePoint in EluNode.PointsTable:
            point = NodePoint.GetVecDataAsTuple()
            points.append(Vector(point))

        scene.objects.active = mesh_obj
        mesh.from_pydata(points, [], faces)

        mesh.transform(EluNode.BlenderGlobalMatrix)

        # Create empty vertex groups
        vertex_groups = {}
        for bone_id in range(len(EluNode.BoneTableIndices)):
            bone_name = elu_mesh_obj.EluMeshNodes[EluNode.BoneTableIndices[bone_id]].NodeName
            vertex_groups[bone_name] = []

        # Add bone weight info
        for PhysiqueInfo in EluNode.PhysiqueTable:
            for PhysiqueSubData in PhysiqueInfo.PhysiqueSubDatas:
                bone_id = PhysiqueSubData.cid
                bone_name = elu_mesh_obj.EluMeshNodes[EluNode.BoneTableIndices[bone_id]].NodeName
                if bone_name in vertex_groups:
                    vertex_index = EluNode.PhysiqueTable.index(PhysiqueInfo)
                    vertex_groups[bone_name].append((vertex_index, PhysiqueSubData.weight))

        # If there is no bone weight info, all vertexes are weighted on current bone equally
        if len(EluNode.BoneTableIndices) == 0:
            vertex_groups[EluNode.NodeName] = []
            for vertex_index in range(len(EluNode.PointsTable)):
                vertex_groups[EluNode.NodeName].append((vertex_index, 1))

        for name, vertex_weight_info in vertex_groups.items():
            group = mesh_obj.vertex_groups.new(name)
            for (vertex_index, weight) in vertex_weight_info:
                group.add([vertex_index], weight, "REPLACE")

        # Apply bone weight modifier
        modifier = mesh_obj.modifiers.new(mesh_name + '-modifier', "ARMATURE")
        modifier.object = armature_object
        modifier.use_vertex_groups = True

        """
        UV Map the mesh
        """
        # mesh_has_extra_uv = False
        # if len(EluNode.TexCoordExtraTable) > 0:
        #     mesh_has_extra_uv = True

        # Not going to include extra uv layer right now.
        mesh_has_extra_uv = False

        # add materials to mesh
        for blender_mat in blender_materials:
            mesh.materials.append(blender_mat)

        scene = bpy.context.scene
        scene.objects.active = mesh_obj
        mesh_obj.select = True

        # Add uv map if and only if TextCoordTable contains any UVs
        if len(EluNode.TexCoordTable) > 0:
            if bpy.ops.object.mode_set.poll():
                bpy.ops.object.mode_set(mode="EDIT")
            else:
                print("mode_set() context is incorrect. Current mode is: {0}".format(bpy.context.mode))
                return
            bm = bmesh.from_edit_mesh(mesh)
            uv_layer = bm.loops.layers.uv.verify()
            if mesh_has_extra_uv:
                uv_layer_extra = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()

            face_index = 0
            for face in bm.faces:
                face.smooth = 1
                if EluNode.PolygonTable[face_index].MaterialID < 0:
                    pass
                elif EluNode.PolygonTable[face_index].MaterialID >= len(blender_materials):
                    pass
                else:
                    face.material_index = EluNode.PolygonTable[face_index].MaterialID

                corner_index = 0
                for loop in face.loops:
                    loop_uv = loop[uv_layer]
                    if mesh_has_extra_uv:
                        loop_uv_extra = loop[uv_layer_extra]

                    polygon = EluNode.PolygonTable[face_index]
                    face_sub_data = polygon.FaceSubDatas[corner_index]
                    uv_index = face_sub_data.uv
                    try:
                        elu_uv = EluNode.TexCoordTable[uv_index].GetVecDataAsTuple()
                    except IndexError:
                        print("Length of TexCoordTable : {0}, uv_index: {1}".format(len(EluNode.TexCoordTable), uv_index))
                        print("Elu Version: {0}".format(elu_mesh_obj.EluHeader.Version))
                        raise AssertionError
                    blender_uv = [elu_uv[0], 1 - elu_uv[1]]
                    loop_uv.uv = blender_uv

                    if mesh_has_extra_uv:
                        uv_extra_index = face_sub_data.uv2
                        elu_uv_extra = EluNode.TexCoordExtraTable[uv_extra_index].GetVecDataAsTuple()
                        blender_uv_extra = [elu_uv_extra[0], 1 - elu_uv_extra[1]]
                        loop_uv_extra.uv = blender_uv_extra
                    corner_index += 1

                face_index += 1

            bmesh.update_edit_mesh(mesh)
            bpy.ops.object.mode_set(mode="OBJECT")

