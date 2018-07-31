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
