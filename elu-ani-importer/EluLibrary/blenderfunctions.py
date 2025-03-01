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
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection, do_unlink=True)

    for action in bpy.data.actions:
        bpy.data.actions.remove(action, do_unlink=True)

    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh, do_unlink=True)

    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature, do_unlink=True)

    for material in bpy.data.materials:
        bpy.data.materials.remove(material, do_unlink=True)

    for scene in bpy.data.scenes:
        for obj in scene.objects:
            scene.objects.unlink(obj, do_unlink=True)

    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def reload_blender():
    bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)


def set_active_blender_object(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.context.view_layer.update()


def draw_elu_skeleton(elu_mesh_obj):
    armature = bpy.data.armatures.new("root_armature")
    armature_obj = bpy.data.objects.new("armature_obj", armature)

    new_collection = bpy.data.collections.new("raiderz")
    new_collection.objects.link(armature_obj)

    current_scene = bpy.context.scene
    current_scene.collection.children.link(new_collection)

    # current_scene.objects.link(armature_obj)
    # current_scene.objects.active = armature_obj

    armature_obj.select_set(True)
    armature.display_type = "STICK"
    # armature_obj.show_x_ray = True
    armature.show_names = True

    set_active_blender_object(armature_obj)

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="EDIT")
    else:
        print("mode_set() context is incorrect. Current mode is: {0}".format(bpy.context.mode))
        return

    for EluMeshNode in elu_mesh_obj.EluMeshNodes:
        EluMeshNode.BlenderLocalMatrix = Matrix(EluMeshNode.LocalMatrix.get_matrix_as_tuples())
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
                    # EluMeshNode.BlenderGlobalMatrix = edit_bone.parent.matrix * EluMeshNode.BlenderLocalMatrix
                    EluMeshNode.BlenderGlobalMatrix = edit_bone.parent.matrix @ EluMeshNode.BlenderLocalMatrix
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

        # scene = bpy.context.scene
        out_collection = None
        for collection in bpy.data.collections:
            out_collection = collection
        out_collection.objects.link(mesh_obj)
        # scene.objects.link(mesh_obj)

        faces = []
        for Polygon in EluNode.PolygonTable:
            face = []
            for FaceSubData in Polygon.FaceSubDatas:
                face.append(FaceSubData.p)
            faces.append(face)

        points = []
        for NodePoint in EluNode.PointsTable:
            point = NodePoint.get_vec_data_as_tuple()
            points.append(Vector(point))

        bpy.context.view_layer.update()
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.context.view_layer.update()
        # scene.objects.active = mesh_obj

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
            group = mesh_obj.vertex_groups.new(name=name)
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

        # scene = bpy.context.scene
        # scene.objects.active = mesh_obj

        bpy.context.view_layer.update()
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.context.view_layer.update()
        mesh_obj.select_set(True)

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
            # bm.faces.layers.tex.verify()
            # @todo for the line above?

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
                        elu_uv = EluNode.TexCoordTable[uv_index].get_vec_data_as_tuple()
                    except IndexError:
                        print(
                            "Length of TexCoordTable : {0}, uv_index: {1}".format(len(EluNode.TexCoordTable), uv_index))
                        print("Elu Version: {0}".format(elu_mesh_obj.EluHeader.version))
                        raise AssertionError
                    blender_uv = [elu_uv[0], 1 - elu_uv[1]]
                    loop_uv.uv = blender_uv

                    if mesh_has_extra_uv:
                        uv_extra_index = face_sub_data.uv2
                        elu_uv_extra = EluNode.TexCoordExtraTable[uv_extra_index].get_vec_data_as_tuple()
                        blender_uv_extra = [elu_uv_extra[0], 1 - elu_uv_extra[1]]
                        loop_uv_extra.uv = blender_uv_extra
                    corner_index += 1

                face_index += 1

            bmesh.update_edit_mesh(mesh)
            bpy.ops.object.mode_set(mode="OBJECT")


def load_and_export_animations(elu_mesh_obj, animations, raider_file_obj):
    # Skeleton
    armature_object = None
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            armature_object = obj

    for animation in animations:
        ani_mesh_obj = FAniMesh(animation)
        ani_mesh_obj.load_and_parse_ani_file()

        if ani_mesh_obj._ani_header.ani_type == datatypes.EAnimationType.RAniType_Bone:
            scene = bpy.context.scene
            scene.frame_start = 0
            scene.frame_end = ani_mesh_obj._ani_header.max_frame
            set_active_blender_object(armature_object)

            animation_basename = os.path.basename(animation)
            action_name = animation_basename.split('.')[0].strip()

            if armature_object.animation_data is None:
                armature_object.animation_data_create()
            else:
                bpy.ops.object.mode_set(mode="POSE")
                for bone in armature_object.pose.bones:
                    armature_object.data.bones[bone.name].select = True

                bpy.ops.pose.rot_clear()
                bpy.ops.pose.scale_clear()
                bpy.ops.pose.transforms_clear()

                armature_object.animation_data_clear()
                armature_object.animation_data_create()
                bpy.ops.object.mode_set(mode="OBJECT")

            action = bpy.data.actions.new(action_name)
            armature_object.animation_data.action = action

            pose = armature_object.pose

            bpy.ops.object.mode_set(mode="POSE")

            for EluNode in elu_mesh_obj.EluMeshNodes:
                if EluNode.BaseVisibility == 0:
                    pose_bone = pose.bones[EluNode.NodeName]
                    pose_bone.scale = Vector((0.001, 0.001, 0.001))
                    pose_bone.keyframe_insert(data_path='scale',
                                              frame=0,
                                              group=EluNode.NodeName)

            # Root motion
            """
            for AniNode in ani_mesh_obj.AniMeshNodes:
                if AniNode.Name == "dummy_loc":
                    try:
                        pose_bone = pose.bones[AniNode.Name]
                        default_armature_object_inverted_world_matrix = armature_object.matrix_world.inverted()

                        for i in range(AniNode.PositionKeyTrack.Count):
                            try:
                                frame = AniNode.PositionKeyTrack.Data[i].Frame / 160
                            except IndexError:
                                print("index: ", i, ", length of positionkeytrack", len(AniNode.PositionKeyTrack.Data), ", count: ", AniNode.PositionKeyTrack.Count)
                                raise Exception
                            elu_position = AniNode.PositionKeyTrack.Data[i].Vector
                            position_vector = Vector(elu_position.get_vec_data_as_tuple())

                            pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                            matrix_diff = default_armature_object_inverted_world_matrix * pbone_matrix_inverted * position_vector
                            armature_object.location = matrix_diff

                            armature_object.keyframe_insert(data_path="location",
                                                            frame=frame,
                                                            group=armature_object.name)

                        for i in range(AniNode.RotationKeyTrack.Count):
                            try:
                                frame = AniNode.RotationKeyTrack.Data[i].Frame / 160
                            except IndexError:
                                print("index: ", i, ", length of positionkeytrack", len(AniNode.PositionKeyTrack.Data), ", count: ", AniNode.PositionKeyTrack.Count)
                                raise Exception
                            elu_quat = AniNode.RotationKeyTrack.Data[i].Quat
                            rot_quat = Quaternion((elu_quat.W, elu_quat.X, elu_quat.Y, elu_quat.Z))
                            pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                            diff_quat = pbone_quat_inverted * rot_quat
                            armature_object.rotation_quaternion = diff_quat

                            armature_object.keyframe_insert(data_path='rotation_quaternion',
                                                            frame=frame,
                                                            group=armature_object.name)
                    except Exception:
                        pass
            """
            for AniNode in ani_mesh_obj._ani_mesh_nodes:
                try:
                    pose_bone = pose.bones[AniNode.Name]
                except Exception:
                    print("Couldn't find pose bone: ", AniNode.Name)
                    continue

                frame = 0
                elu_position = AniNode.BaseTranslation
                if elu_position:
                    position_vector = Vector(elu_position.get_vec_data_as_tuple())
                    if pose_bone.parent:
                        result = pose_bone.parent.matrix @ position_vector
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        matrix_diff = armature_matrix_inverse @ pbone_matrix_inverted @ result
                        pose_bone.location = matrix_diff
                    else:
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        # matrix_diff = armature_matrix_inverse * pbone_matrix_inverted * position_vector
                        matrix_diff = armature_matrix_inverse @ pbone_matrix_inverted @ position_vector
                        pose_bone.location = matrix_diff

                    pose_bone.keyframe_insert(data_path="location",
                                              frame=frame,
                                              group=AniNode.Name)

                for i in range(AniNode.PositionKeyTrack.Count):
                    try:
                        frame = AniNode.PositionKeyTrack.Data[i].Frame / 160
                    except IndexError:
                        print("index: ", i, ", length of positionkeytrack", len(AniNode.PositionKeyTrack.Data),
                              ", count: ", AniNode.PositionKeyTrack.Count)
                        raise Exception
                    elu_position = AniNode.PositionKeyTrack.Data[i].Vector
                    position_vector = Vector(elu_position.get_vec_data_as_tuple())
                    if pose_bone.parent:
                        result = pose_bone.parent.matrix @ position_vector
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        matrix_diff = armature_matrix_inverse @ pbone_matrix_inverted @ result
                        pose_bone.location = matrix_diff
                    else:
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        matrix_diff = armature_matrix_inverse @ pbone_matrix_inverted @ position_vector
                        pose_bone.location = matrix_diff

                    pose_bone.keyframe_insert(data_path="location",
                                              frame=frame,
                                              group=AniNode.Name)

                frame = 0
                elu_quat = AniNode.BaseRotation
                if elu_quat:
                    rot_quat = Quaternion((elu_quat.W, elu_quat.X, elu_quat.Y, elu_quat.Z))
                    if pose_bone.parent:
                        result_quat = pose_bone.parent.matrix.to_quaternion() @ rot_quat
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted @ result_quat
                        pose_bone.rotation_quaternion = diff_quat
                    else:
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted @ rot_quat
                        pose_bone.rotation_quaternion = diff_quat

                    pose_bone.keyframe_insert(data_path='rotation_quaternion',
                                              frame=frame,
                                              group=AniNode.Name)

                for i in range(AniNode.RotationKeyTrack.Count):
                    frame = AniNode.RotationKeyTrack.Data[i].Frame / 160
                    elu_quat = AniNode.RotationKeyTrack.Data[i].Quat
                    rot_quat = Quaternion((elu_quat.W, elu_quat.X, elu_quat.Y, elu_quat.Z))
                    if pose_bone.parent:
                        result_quat = pose_bone.parent.matrix.to_quaternion() @ rot_quat
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted @ result_quat
                        pose_bone.rotation_quaternion = diff_quat
                    else:
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted @ rot_quat
                        pose_bone.rotation_quaternion = diff_quat
                    pose_bone.keyframe_insert(data_path='rotation_quaternion',
                                              frame=frame,
                                              group=AniNode.Name)

                frame = 0
                elu_scale = AniNode.BaseScale
                if elu_scale:
                    elu_scale = AniNode.BaseScale
                    pose_bone.keyframe_insert(data_path="scale",
                                              frame=frame,
                                              group=AniNode.Name)

                for i in range(AniNode.ScaleKeyTrack.Count):
                    frame = AniNode.ScaleKeyTrack.Data[i].Frame / 160
                    elu_scale = AniNode.ScaleKeyTrack.Data[i].Vector

                    scale_vector = Vector(elu_scale.get_vec_data_as_tuple())
                    pose_bone.scale = scale_vector
                    pose_bone.keyframe_insert(data_path="scale",
                                              frame=frame,
                                              group=AniNode.Name)

                # Begin visibility keyframes fix
                source_frames = []
                source_viskeys = []
                for i in range(AniNode.VisKeyTrack.Count):
                    frame = AniNode.VisKeyTrack.Data[i].Frame / 160
                    vis_key = AniNode.VisKeyTrack.Data[i].Vis
                    source_frames.append(frame)
                    source_viskeys.append(vis_key)

                final_frames, final_viskeys = generate_viskeys(source_frames, source_viskeys)

                # Reset AniNode viskey data
                AniNode.VisKeyTrack.Count = len(final_frames)
                AniNode.VisKeyTrack.Data = []
                for i in range(len(final_frames)):
                    VisKey = datatypes.FVisKey()
                    VisKey.Frame = final_frames[i]
                    VisKey.Vis = final_viskeys[i]
                    AniNode.VisKeyTrack.Data.append(VisKey)

                # End visibility keyframes fix

                for i in range(AniNode.VisKeyTrack.Count):
                    frame = AniNode.VisKeyTrack.Data[i].Frame
                    vis_key = AniNode.VisKeyTrack.Data[i].Vis

                    SET_VISKEY = False
                    if 0 <= int(frame) <= ani_mesh_obj._ani_header.max_frame:
                        if int(frame) == 0:
                            if round(vis_key) == 0:
                                if pose_bone.scale == Vector((1, 1, 1)):
                                    # pose_bone.scale = Vector((0.001, 0.001, 0.001))
                                    pose_bone.scale = Vector((0, 0, 0))
                                    SET_VISKEY = True
                            elif round(vis_key) == 1:
                                # if pose_bone.scale == Vector((0.001, 0.001, 0.001)):
                                if pose_bone.scale == Vector((0, 0, 0)):
                                    pose_bone.scale = Vector((1, 1, 1))
                                    SET_VISKEY = True
                        elif int(frame) == ani_mesh_obj._ani_header.max_frame:
                            if round(vis_key) == 0:
                                # if pose_bone.scale == Vector((0.001, 0.001, 0.001)):
                                #    pose_bone.scale = Vector((0.001, 0.001, 0.001))
                                if pose_bone.scale == Vector((0, 0, 0)):
                                    pose_bone.scale = Vector((0, 0, 0))
                                    SET_VISKEY = True
                            elif round(vis_key) == 1:
                                if pose_bone.scale == Vector((1, 1, 1)):
                                    pose_bone.scale = Vector((1, 1, 1))
                                    SET_VISKEY = True
                        else:
                            current_frame = int(frame)
                            previous_frame = int(AniNode.VisKeyTrack.Data[i - 1].Frame / 160)
                            # previous_frame = current_frame - 1

                            if current_frame == previous_frame:
                                frame += 1
                                if round(vis_key) == 0:
                                    # pose_bone.scale = Vector((0.001, 0.001, 0.001))
                                    pose_bone.scale = Vector((0, 0, 0))
                                    SET_VISKEY = True
                                elif round(vis_key) == 1:
                                    pose_bone.scale = Vector((1, 1, 1))
                                    SET_VISKEY = True
                            else:
                                if round(vis_key) == 0:
                                    # pose_bone.scale = Vector((0.001, 0.001, 0.001))
                                    pose_bone.scale = Vector((0, 0, 0))
                                    SET_VISKEY = True
                                elif round(vis_key) == 1:
                                    pose_bone.scale = Vector((1, 1, 1))
                                    SET_VISKEY = True
                    else:
                        pass

                    if SET_VISKEY is True:
                        pose_bone.keyframe_insert(data_path="scale",
                                                  frame=frame,
                                                  group=AniNode.Name)

            # Begin rotation bug (MBAE-3) fix

            """
            fcurves = armature_object.animation_data.action.fcurves
            for fcurve in fcurves:
                for kf in fcurve.keyframe_points:
                    kf.interpolation = "CONSTANT"
            """
            # End rotation bug (MBAE-3) fix

            bpy.ops.object.mode_set(mode="OBJECT")

            if os.path.exists(raider_file_obj.object_ani_folder):
                assert os.path.isdir(raider_file_obj.object_ani_folder)
            else:
                os.makedirs(raider_file_obj.object_ani_folder)
            dest_filepath = raider_file_obj.object_ani_folder + os.sep + "A_" + action_name + ".fbx"

            try:
                bpy.ops.export_scene.fbx(filepath=dest_filepath,
                                         check_existing=True,
                                         apply_scale_options='FBX_SCALE_UNITS',
                                         object_types={"ARMATURE"})

                bpy.data.actions.remove(action, do_unlink=True)
            except Exception:
                print(action_name, " failed to export")

            # Following line prevents animations from glitching out when mass exporting animations with root motion.
            armature_object.matrix_world = Matrix.Identity(4)

        else:
            # @todo vertex animation
            scene = bpy.context.scene
            scene.frame_start = 0
            scene.frame_end = ani_mesh_obj._ani_header.max_frame

            for AniNode in ani_mesh_obj._ani_mesh_nodes:
                mesh = None
                try:
                    mesh_obj = bpy.data.objects[AniNode.Name + '-mesh']
                    mesh = mesh_obj.data
                    print("\n\nmesh found\n\n", AniNode.Name)
                except:
                    continue

                scene.objects.active = mesh_obj

                animation_basename = os.path.basename(animation)
                action_name = animation_basename.split('.')[0].strip()
                action = bpy.data.actions.new(action_name)

                mesh.animation_data_create()
                mesh.animation_data.action = action

                data_path = "vertices[%d].co"
                vec_z = Vector((0.0, 0.0, 1.0))

                """
                if bpy.ops.object.mode_set.poll():
                    bpy.ops.object.mode_set(mode="EDIT")
                else:
                    print("mode_set() context is incorrect. Current mode is: {0}".format(bpy.context.mode))
                    return
                
                bm = bmesh.from_edit_mesh(mesh)

                bpy.ops.object.mode_set(mode="OBJECT")
                """


def export_mesh(raider_file_obj, elu_mesh_obj):
    if os.path.exists(raider_file_obj.object_model_folder):
        assert os.path.isdir(raider_file_obj.object_model_folder)
    else:
        os.makedirs(raider_file_obj.object_model_folder)

    if raider_file_obj.has_animations():
        dest_filepath = raider_file_obj.object_model_folder + os.sep + "SK_" + raider_file_obj.object_name + ".fbx"
        # else:
        #   dest_filepath = raider_file_obj.object_model_folder + os.sep + "S_" + raider_file_obj.object_name + ".fbx"

        # if raider_file_obj.has_animations():
        obj_types = {"ARMATURE", "MESH"}
        bpy.ops.export_scene.fbx(filepath=dest_filepath,
                                 check_existing=True,
                                 use_selection=False,
                                 apply_scale_options='FBX_SCALE_UNITS',
                                 object_types=obj_types,
                                 bake_anim=True)
    else:
        obj_types = {"MESH"}
        # current_scene = bpy.context.scene

        LOD_Indices = set()
        for EluNode in elu_mesh_obj.EluMeshNodes:
            # print(EluNode.NodeName, EluNode.LODProjectIndex)
            LOD_Indices.add(EluNode.LODProjectIndex)

        for index in LOD_Indices:
            for obj in bpy.data.objects:
                obj.select_set(False)

            for EluNode in elu_mesh_obj.EluMeshNodes:
                if EluNode.LODProjectIndex == index:
                    for obj in bpy.data.objects:
                        if obj.name == EluNode.NodeName + "-mesh":
                            obj.select_set(True)
            dest_filepath = raider_file_obj.object_model_folder + os.sep + "S_" + \
                            raider_file_obj.object_name + "_LOD" + str(index) + ".fbx"

            bpy.ops.export_scene.fbx(filepath=dest_filepath,
                                     check_existing=True,
                                     use_selection=True,
                                     apply_scale_options='FBX_SCALE_UNITS',
                                     object_types=obj_types,
                                     bake_anim=False)


def export_only_skeletal_meshes(raider_file_obj, elu_mesh_obj):
    if os.path.exists(raider_file_obj.object_model_folder):
        assert os.path.isdir(raider_file_obj.object_model_folder)
    else:
        os.makedirs(raider_file_obj.object_model_folder)

    dest_filepath = raider_file_obj.object_model_folder + os.sep + "SK_" + raider_file_obj.object_name + ".fbx"

    # if raider_file_obj.has_animations():
    obj_types = {"ARMATURE", "MESH"}
    bpy.ops.export_scene.fbx(filepath=dest_filepath,
                             check_existing=True,
                             use_selection=False,
                             apply_scale_options='FBX_SCALE_UNITS',
                             object_types=obj_types,
                             bake_anim=True)


def export_modular_skeletal_meshses(raider_file_obj, elu_mesh_obj):
    if os.path.exists(raider_file_obj.object_model_folder):
        assert os.path.isdir(raider_file_obj.object_model_folder)
    else:
        os.makedirs(raider_file_obj.object_model_folder)

    # MODULAR_PARTS = ["hair", "chest", "hands", "legs", "feet", "Dummy_eyes",
    #                 "hat_item", "chest_item", "hands_item", "legs_item", "feet_item", "back_item"]

    MODULAR_PARTS = ["hair", "chest", "hands", "legs", "feet", "back", "hat", "Dummy_eyes", "face"]
    # MODULAR_PARTS = ["hair", "chest", "hands", "legs", "feet", "Dummy_eyes", "back_item"]

    modular_part_found = False
    for item_name in MODULAR_PARTS:
        for obj in bpy.data.objects:
            obj.select_set(False)
        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                obj.select_set(True)
                amt = obj.data
                for bone in amt.bones:
                    bone.select = True
        mesh_found = False
        for obj in bpy.data.objects:
            if obj.name == item_name + '-mesh' or obj.name == item_name + "_item" + '-mesh':
                obj.select_set(True)
                mesh_found = True
                modular_part_found = True

        dest_filepath = raider_file_obj.object_model_folder + os.sep + "SK_" + raider_file_obj.object_name + "_" + item_name + ".fbx"

        if mesh_found:
            obj_types = {"ARMATURE", "MESH"}
            bpy.ops.export_scene.fbx(filepath=dest_filepath,
                                     check_existing=True,
                                     use_selection=True,
                                     apply_scale_options='FBX_SCALE_UNITS',
                                     object_types=obj_types,
                                     bake_anim=True)
    if not modular_part_found:
        # if the for loop didn't break
        dest_filepath = raider_file_obj.object_model_folder + os.sep + "SK_" + raider_file_obj.object_name + ".fbx"
        obj_types = {"ARMATURE", "MESH"}
        bpy.ops.export_scene.fbx(filepath=dest_filepath,
                                 check_existing=True,
                                 use_selection=False,
                                 apply_scale_options='FBX_SCALE_UNITS',
                                 object_types=obj_types,
                                 bake_anim=True)


def export_xml_files(raider_file_obj):
    if os.path.exists(raider_file_obj.object_xml_folder):
        assert os.path.isdir(raider_file_obj.object_xml_folder)
    else:
        os.makedirs(raider_file_obj.object_xml_folder)

    if raider_file_obj.elu_xml_file:
        filename = os.path.basename(raider_file_obj.elu_xml_file)
        dest_path = raider_file_obj.object_xml_folder + os.sep + filename
        shutil.copyfile(raider_file_obj.elu_xml_file, dest_path)

    if raider_file_obj.animation_xml_file:
        filename = os.path.basename(raider_file_obj.animation_xml_file)
        dest_path = raider_file_obj.object_xml_folder + os.sep + filename
        shutil.copyfile(raider_file_obj.animation_xml_file, dest_path)

    if raider_file_obj.animation_event_xml_file:
        filename = os.path.basename(raider_file_obj.animation_event_xml_file)
        dest_path = raider_file_obj.object_xml_folder + os.sep + filename
        shutil.copyfile(raider_file_obj.animation_event_xml_file, dest_path)

    if raider_file_obj.animation_info_xml_file:
        filename = os.path.basename(raider_file_obj.animation_info_xml_file)
        dest_path = raider_file_obj.object_xml_folder + os.sep + filename
        shutil.copyfile(raider_file_obj.animation_info_xml_file, dest_path)

    if raider_file_obj.animation_sound_event_xml_file:
        filename = os.path.basename(raider_file_obj.animation_sound_event_xml_file)
        dest_path = raider_file_obj.object_xml_folder + os.sep + filename
        shutil.copyfile(raider_file_obj.animation_sound_event_xml_file, dest_path)

    if raider_file_obj.scene_xml_file:
        filename = os.path.basename(raider_file_obj.scene_xml_file)
        dest_path = raider_file_obj.object_xml_folder + os.sep + filename
        shutil.copyfile(raider_file_obj.scene_xml_file, dest_path)


def generate_viskeys(frames_list, viskeys_list):
    """
    Generates proper viskeys for blender from .ani viskeys
    """
    result_set = set()
    index = 0
    while index < len(frames_list):
        current_keyframe = int(frames_list[index])
        current_viskey = round(viskeys_list[index])

        try:
            next_keyframe = int(frames_list[index + 1])
            next_viskey = round(viskeys_list[index + 1])
        except:
            break
        # print("Current_keyframe: {0}, next_keyframe: {1}, current_viskey: {2}, next_viskey: {3}".format(current_keyframe, next_keyframe, current_viskey, next_viskey))

        if current_keyframe == next_keyframe:
            try:
                assert current_viskey != next_viskey
            except AssertionError:
                # @todo handle assertion error
                pass
            next_keyframe = current_keyframe + 1
            result_set.add((current_keyframe, current_viskey))
            result_set.add((next_keyframe, next_viskey))
            index += 1
        else:
            if current_viskey == next_viskey:
                try:
                    previous_keyframe = int(frames_list[index - 1])
                    previous_viskey = round(viskeys_list[index - 1])
                    if previous_keyframe == current_keyframe:
                        current_keyframe += 1
                    else:
                        pass
                    result_set.add((current_keyframe, current_viskey))
                    result_set.add((next_keyframe, next_viskey))
                    index += 1
                except:
                    result_set.add((current_keyframe, current_viskey))
                    result_set.add((next_keyframe, next_viskey))
                    index += 1
            else:
                try:
                    previous_keyframe = int(frames_list[index - 1])
                    previous_viskey = round(viskeys_list[index - 1])

                    if previous_keyframe == current_keyframe:
                        current_keyframe += 1
                    else:
                        pass
                except:
                    pass

                mid_keyframe = next_keyframe - 1
                mid_viskey = current_viskey
                result_set.add((current_keyframe, current_viskey))
                result_set.add((mid_keyframe, mid_viskey))
                result_set.add((next_keyframe, next_viskey))
                index += 1

    result_frames = []
    result_viskeys = []

    for tup in result_set:
        result_frames.append(tup[0])

    result_frames.sort()

    for frame in result_frames:
        for tup in result_set:
            if frame == tup[0]:
                result_viskeys.append(tup[1])

    return result_frames, result_viskeys
