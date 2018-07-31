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

