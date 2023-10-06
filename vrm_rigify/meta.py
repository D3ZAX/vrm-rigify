import bpy
import math

from .base import BASE_IGNORED, FINGER_BONES, create_bone_mapping, create_edit_bone_mapping, objects_by_patterns
from .debug import LOGGER
from .other import editing

BONES_DELETE = [
    'pelvis',
    'palm.01',
    'palm.02',
    'palm.03',
    'palm.04',
]

META_IGNORED = BASE_IGNORED + [
    # Assumed to be in correct position by default.
    'heel.02',
    # Unneeded facial features.
    # Expressions managed by shape keys.
    'face',
    'teeth',
]

LIMB_BONES = [
    'upper_arm',
    'thigh',
]

SUPER_FINGER_BONES = [
    'f_pinky.01',
    'f_ring.01',
    'f_middle.01',
    'f_index.01',
    'thumb.01',
]

def fix_vrm_bone(vroid_rig):
    with editing(vroid_rig):
        edit_bones = vroid_rig.data.edit_bones
        SPINE_BONES = ["Hips", "Spine", "Chest", "UpperChest", "Neck"]
        for i in range(len(SPINE_BONES) - 1):
            tail_bone = edit_bones[SPINE_BONES[i]]
            head_bone = edit_bones[SPINE_BONES[i + 1]]
            tail_bone.tail = head_bone.head
            head_bone.use_connect = True
        LEG_BONES = ["UpperLeg_{}", "LowerLeg_{}", "Foot_{}", "ToeBase_{}"]
        for i in range(len(LEG_BONES) - 1):
            tail_bone_l = edit_bones[LEG_BONES[i].format("L")]
            head_bone_l = edit_bones[LEG_BONES[i + 1].format("L")]
            tail_bone_l.tail = head_bone_l.head
            head_bone_l.use_connect = True
            tail_bone_r = edit_bones[LEG_BONES[i].format("R")]
            head_bone_r = edit_bones[LEG_BONES[i + 1].format("R")]
            tail_bone_r.tail = head_bone_r.head
            head_bone_r.use_connect = True
        
        edit_bones["Foot_L"].tail = edit_bones["ToeBase_L"].head
        edit_bones["ToeBase_L"].use_connect = True
        edit_bones["Foot_R"].tail = edit_bones["ToeBase_R"].head
        edit_bones["ToeBase_R"].use_connect = True
        
        for finger_name in FINGER_BONES:
            bone_finger_l1 = edit_bones[finger_name.format(1, "L")]
            bone_finger_l2 = edit_bones[finger_name.format(2, "L")]
            bone_finger_l3 = edit_bones[finger_name.format(3, "L")]
            bone_finger_r1 = edit_bones[finger_name.format(1, "R")]
            bone_finger_r2 = edit_bones[finger_name.format(2, "R")]
            bone_finger_r3 = edit_bones[finger_name.format(3, "R")]
            center = (bone_finger_l1.head + bone_finger_l2.head + bone_finger_l3.head) / 3
            bone_finger_l2.use_connect = False
            bone_finger_l3.use_connect = False
            if finger_name == FINGER_BONES[0]:
                line = bone_finger_l3.tail - bone_finger_l1.head
                line_len = line.length
                line_dir = line / line_len
                mid = (bone_finger_l2.head + bone_finger_l3.head) * 0.5
                off = mid - bone_finger_l1.head
                off_project_len = line.dot(off) / line_len
                vertical_point = line_dir * off_project_len + bone_finger_l1.head
                vertical_dir = (mid - vertical_point).normalized()
                off_project_len = line.dot(bone_finger_l2.head - bone_finger_l1.head) / line_len
                vertical_point = line_dir * off_project_len + bone_finger_l1.head
                bone_finger_l2.head = vertical_point + vertical_dir * 0.001
                off_project_len = line.dot(bone_finger_l3.head - bone_finger_l1.head) / line_len
                vertical_point = line_dir * off_project_len + bone_finger_l1.head
                bone_finger_l3.head = vertical_point + vertical_dir * 0.001
            else:
                bone_finger_l1.head.y = center.y
                bone_finger_l1.head.z = center.z - 0.0005
                bone_finger_l2.head.y = center.y
                bone_finger_l2.head.z = center.z + 0.001
                bone_finger_l3.head.y = center.y
                bone_finger_l3.head.z = center.z + 0.001
                bone_finger_l3.tail.y = center.y
                bone_finger_l3.tail.z = center.z - 0.0005
                
            bone_finger_l1.tail = bone_finger_l2.head
            bone_finger_l2.tail = bone_finger_l3.head
            bone_finger_l2.use_connect = True
            bone_finger_l3.use_connect = True
            bone_finger_r1.head = bone_finger_l1.head
            bone_finger_r1.head.x = -bone_finger_r1.head.x
            bone_finger_r1.tail = bone_finger_l1.tail
            bone_finger_r1.tail.x = -bone_finger_r1.tail.x
            bone_finger_r2.use_connect = False
            bone_finger_r3.use_connect = False
            bone_finger_r2.head = bone_finger_l2.head
            bone_finger_r2.head.x = -bone_finger_r2.head.x
            bone_finger_r2.tail = bone_finger_l2.tail
            bone_finger_r2.tail.x = -bone_finger_r2.tail.x
            bone_finger_r3.head = bone_finger_l3.head
            bone_finger_r3.head.x = -bone_finger_r3.head.x
            bone_finger_r3.tail = bone_finger_l3.tail
            bone_finger_r3.tail.x = -bone_finger_r3.tail.x
            bone_finger_r2.use_connect = True
            bone_finger_r3.use_connect = True

            #if finger_name == FINGER_BONES[0]:
                #bone_finger_l1.roll = math.radians(80)
                #bone_finger_l2.roll = math.radians(80)
                #bone_finger_l3.roll = math.radians(80)
                #bone_finger_r1.roll = math.radians(-80)
                #bone_finger_r2.roll = math.radians(-80)
                #bone_finger_r3.roll = math.radians(-80)
            #else:
                #bone_finger_l1.roll = math.radians(180)
                #bone_finger_l2.roll = math.radians(180)
                #bone_finger_l3.roll = math.radians(180)
                #bone_finger_r1.roll = math.radians(-180)
                #bone_finger_r2.roll = math.radians(-180)
                #bone_finger_r3.roll = math.radians(-180)

def meta_rig_base_bones(meta_rig):
    for bone in meta_rig.data.edit_bones:
        if objects_by_patterns([bone], META_IGNORED):
            LOGGER.info(f"ignoring bone '{bone.name}'")
            continue
        yield bone


def position_meta_rig(meta_rig, vroid_rig):
    with editing(meta_rig, vroid_rig):
        base_bones = meta_rig_base_bones(meta_rig)
        conversions = create_edit_bone_mapping(base_bones, vroid_rig)

        # Position meta rig and move bones.
        meta_rig.matrix_world = vroid_rig.matrix_world
        for meta_bone, vroid_bone in conversions:
            LOGGER.info(f"positioning '{meta_bone.name}' to '{vroid_bone.name}'")
            meta_bone.select = True
            meta_bone.head = vroid_bone.head
            meta_bone.tail = vroid_bone.tail
            meta_bone.roll = vroid_bone.roll


# Note: transforms on the VRoid model must *not* be
# applied for the generated rig to be positioned correctly.
def generate_meta_rig(vroid_rig):
    # Simplify VRoid bone names.
    LOGGER.info("simplifying VRoid bone names")
    bpy.ops.vrm.bones_rename(armature_name=vroid_rig.name)
    
    LOGGER.info("fix VRoid bones")
    fix_vrm_bone(vroid_rig)

    # Spawn meta-rig.
    LOGGER.info("creating and positioning meta-rig")
    bpy.ops.object.armature_human_metarig_add()
    meta_rig = bpy.context.view_layer.objects.active
    meta_rig.name = f"{vroid_rig.name}.metarig"

    # Remove unneeded bones.
    with editing(meta_rig):
        edit_bones = meta_rig.data.edit_bones
        for bone in objects_by_patterns(edit_bones, BONES_DELETE):
            LOGGER.info(f"deleting meta-rig bone '{bone.name}'")
            edit_bones.remove(bone)

    # Align meta-rig bones with VRoid model.
    position_meta_rig(meta_rig, vroid_rig)

    # Amend armature limbs.
    pose_bones = meta_rig.pose.bones
    for bone in pose_bones:
        bone.rigify_parameters.roll_alignment = "automatic"
    
    for bone in objects_by_patterns(pose_bones, LIMB_BONES):
        LOGGER.info(f"amending bone parameters for limb '{bone.name}'")
        # Amend resultant bone count.
        bone.rigify_parameters.segments = 1
        # Ensure local bend direction is correct.
        bone.rigify_parameters.rotation_axis = 'x'

    ## Amend armature fingers.
    #for bone in objects_by_patterns(pose_bones, SUPER_FINGER_BONES):
        #LOGGER.info(f"amending bone parameters for finger '{bone.name}'")
        # Ensure primary bend direction is correct.
        #bone.rigify_parameters.primary_rotation_axis = 'Z'
        #bone.rigify_parameters.roll_alignment = "automatic"
        #bone.rigify_parameters.primary_rotation_axis = 'X'

    # Return generated meta-rig object.
    LOGGER.info("meta-rig generated")
    return meta_rig
