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


def load_and_export_animations(elu_mesh_obj, animations, raider_file_obj):
    # Skeleton
    armature_object = None
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            armature_object = obj

    for animation in animations:
        ani_mesh_obj = FAniMesh(animation)

        if ani_mesh_obj.AniHeader.AniType == datatypes.EAnimationType.RAniType_Bone:
            scene = bpy.context.scene
            scene.frame_start = 0
            scene.frame_end = ani_mesh_obj.AniHeader.MaxFrame
            scene.objects.active = armature_object

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
                            position_vector = Vector(elu_position.GetVecDataAsTuple())

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

            for AniNode in ani_mesh_obj.AniMeshNodes:
                try:
                    pose_bone = pose.bones[AniNode.Name]
                except Exception:
                    print ("Couldn't find pose bone: ", AniNode.Name)
                    continue

                frame = 0
                elu_position = AniNode.BaseTranslation
                if elu_position:
                    position_vector = Vector(elu_position.GetVecDataAsTuple())
                    if pose_bone.parent:
                        result = pose_bone.parent.matrix * position_vector
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        matrix_diff = armature_matrix_inverse * pbone_matrix_inverted * result
                        pose_bone.location = matrix_diff
                    else:
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        matrix_diff = armature_matrix_inverse * pbone_matrix_inverted * position_vector
                        pose_bone.location = matrix_diff

                    pose_bone.keyframe_insert(data_path="location",
                                            frame=frame,
                                            group=AniNode.Name)

                for i in range(AniNode.PositionKeyTrack.Count):
                    try:
                        frame = AniNode.PositionKeyTrack.Data[i].Frame / 160
                    except IndexError:
                        print("index: ", i, ", length of positionkeytrack", len(AniNode.PositionKeyTrack.Data), ", count: ", AniNode.PositionKeyTrack.Count)
                        raise Exception
                    elu_position = AniNode.PositionKeyTrack.Data[i].Vector
                    position_vector = Vector(elu_position.GetVecDataAsTuple())
                    if pose_bone.parent:
                        result = pose_bone.parent.matrix * position_vector
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        matrix_diff = armature_matrix_inverse * pbone_matrix_inverted * result
                        pose_bone.location = matrix_diff
                    else:
                        armature_matrix_inverse = armature_object.matrix_world.inverted()
                        pbone_matrix_inverted = pose_bone.bone.matrix_local.inverted()
                        matrix_diff = armature_matrix_inverse * pbone_matrix_inverted * position_vector
                        pose_bone.location = matrix_diff

                    pose_bone.keyframe_insert(data_path="location",
                                            frame=frame,
                                            group=AniNode.Name)

                frame = 0
                elu_quat = AniNode.BaseRotation
                if elu_quat:
                    rot_quat = Quaternion((elu_quat.W, elu_quat.X, elu_quat.Y, elu_quat.Z))
                    if pose_bone.parent:
                        result_quat = pose_bone.parent.matrix.to_quaternion() * rot_quat
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted * result_quat
                        pose_bone.rotation_quaternion = diff_quat
                    else:
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted * rot_quat
                        pose_bone.rotation_quaternion = diff_quat

                    pose_bone.keyframe_insert(data_path='rotation_quaternion',
                                            frame=frame,
                                            group=AniNode.Name)

                for i in range(AniNode.RotationKeyTrack.Count):
                    frame = AniNode.RotationKeyTrack.Data[i].Frame / 160
                    elu_quat = AniNode.RotationKeyTrack.Data[i].Quat
                    rot_quat = Quaternion((elu_quat.W, elu_quat.X, elu_quat.Y, elu_quat.Z))
                    if pose_bone.parent:
                        result_quat = pose_bone.parent.matrix.to_quaternion() * rot_quat
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted * result_quat
                        pose_bone.rotation_quaternion = diff_quat
                    else:
                        pbone_quat_inverted = pose_bone.matrix.to_quaternion().inverted()
                        diff_quat = pbone_quat_inverted * rot_quat
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

                    scale_vector = Vector(elu_scale.GetVecDataAsTuple())
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
                    if 0 <= int(frame) <= ani_mesh_obj.AniHeader.MaxFrame:
                        if int(frame) == 0:
                            if round(vis_key) == 0:
                                if pose_bone.scale == Vector((1, 1, 1)):
                                    pose_bone.scale = Vector((0.001, 0.001, 0.001))
                                    SET_VISKEY = True
                            elif round(vis_key) == 1:
                                if pose_bone.scale == Vector((0.001, 0.001, 0.001)):
                                    pose_bone.scale = Vector((1, 1, 1))
                                    SET_VISKEY = True
                        elif int(frame) == ani_mesh_obj.AniHeader.MaxFrame:
                            if round(vis_key) == 0:
                                if pose_bone.scale == Vector((0.001, 0.001, 0.001)):
                                    pose_bone.scale = Vector((0.001, 0.001, 0.001))
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
                                    pose_bone.scale = Vector((0.001, 0.001, 0.001))
                                    SET_VISKEY = True
                                elif round(vis_key) == 1:
                                    pose_bone.scale = Vector((1, 1, 1))
                                    SET_VISKEY = True
                            else:
                                if round(vis_key) == 0:
                                    pose_bone.scale = Vector((0.001, 0.001, 0.001))
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
                                        use_default_take=False,
                                        check_existing=True,
                                        version="ASCII6100",
                                        object_types={"ARMATURE"},
                                        use_anim=True,
                                        use_anim_action_all=True)

                bpy.data.actions.remove(action, do_unlink=True)
            except Exception:
                print(action_name, " failed to export")

            # Following line prevents animations from glitching out when mass exporting animations with root motion.
            armature_object.matrix_world = Matrix.Identity(4)

        else:
            # @todo vertex animation
            scene = bpy.context.scene
            scene.frame_start = 0
            scene.frame_end = ani_mesh_obj.AniHeader.MaxFrame

            for AniNode in ani_mesh_obj.AniMeshNodes:
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

