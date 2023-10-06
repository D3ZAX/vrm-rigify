import mathutils
from .base import FINGER_BONES, objects_by_pattern, objects_by_patterns, create_bone_mapping, BASE_IGNORED
from .debug import LOGGER
from .other import editing, posing

GEN_IGNORED = BASE_IGNORED + [
    'teeth',
]


def remove_gen_rig_ignored_bones(gen_rig):
    with editing(gen_rig):
        edit_bones = gen_rig.data.edit_bones
        ignored = objects_by_patterns(edit_bones, GEN_IGNORED)
        for bone in ignored:
            LOGGER.info(f"deleting bone '{bone.name}'")
            edit_bones.remove(bone)


def fix_gen_rig_constraint(gen_rig):
    with posing(gen_rig):
        pose_bones = gen_rig.pose.bones
        pb = pose_bones["ORG-spine.004"]
        pb.constraints["Stretch To"].subtarget = "head"
        
        #pb = pose_bones["ORG-eye.L"]
        #crc = pb.constraints.new('COPY_TRANSFORMS')
        #crc.target = gen_rig
        #crc.subtarget = "master_eye.L"
        
        #pb = pose_bones["ORG-eye.R"]
        #crc = pb.constraints.new('COPY_TRANSFORMS')
        #crc.target = gen_rig
        #crc.subtarget = "master_eye.R"


def fix_gen_rig_transfrom(vroid_rig, gen_rig):
    TRANSFROM_REF = {"ORG-eye.L":"FaceEye_L",
                    "ORG-eye.R":"FaceEye_R",
                    "master_eye.L":"FaceEye_L",
                    "master_eye.R":"FaceEye_R"}
    with editing(gen_rig, vroid_rig):
        edit_bones = gen_rig.data.edit_bones
        ori_edit_bones = vroid_rig.data.edit_bones
        for name1,name2 in TRANSFROM_REF.items():
            bone = edit_bones[name1]
            ori_bone = ori_edit_bones[name2]
            #bone.head = ori_bone.head
            #bone.tail = ori_bone.tail
            bone.roll = ori_bone.roll
    #with posing(gen_rig, vroid_rig):
        #pose_bones = gen_rig.pose.bones
        #ori_pose_bones = vroid_rig.pose.bones
        #for name1,name2 in TRANSFROM_REF.items():
            #bone = pose_bones[name1]
            #ori_bone = ori_pose_bones[name2]
            #bone.custom_shape_translation = ori_bone.custom_shape_translation


def fix_eye(vroid_rig, gen_rig):
    with editing(gen_rig, vroid_rig):
        edit_bones = gen_rig.data.edit_bones
        ori_edit_bones = vroid_rig.data.edit_bones
        eyes_bone = edit_bones["eyes"]
        l_eye_bone = edit_bones["eye.L"]
        r_eye_bone = edit_bones["eye.R"]
        ori_l_eye = ori_edit_bones["FaceEye_L"]
        
        from_point = l_eye_bone.head
        normal = (eyes_bone.tail - eyes_bone.head).cross(l_eye_bone.head - eyes_bone.head)
        to_point = mathutils.geometry.intersect_line_plane(
            ori_l_eye.head,
            ori_l_eye.tail,
            l_eye_bone.head,
            normal)
        from_off = from_point - eyes_bone.head
        to_off = to_point - eyes_bone.head
        x_ratio = 0 if from_off.x == 0 else to_off.x / from_off.x
        y_ratio = 0 if from_off.y == 0 else to_off.y / from_off.y
        z_ratio = 0 if from_off.z == 0 else to_off.z / from_off.z
        ratio = max(x_ratio, y_ratio, z_ratio)
        off = eyes_bone.tail - eyes_bone.head
        off *= ratio
        eyes_bone.tail = eyes_bone.head + off
        off = (l_eye_bone.tail - l_eye_bone.head) * ratio
        l_eye_bone.head = to_point
        l_eye_bone.tail = l_eye_bone.head + off
        r_eye_bone.head = l_eye_bone.head
        r_eye_bone.head.x = -r_eye_bone.head.x
        r_eye_bone.tail = l_eye_bone.tail
        r_eye_bone.tail.x = -r_eye_bone.tail.x
        

def gen_rig_base_bones(gen_rig):
    for bone in gen_rig.data.bones:
        # Rigify eyes are not deforming by default.
        deform = bone.name.startswith('DEF')
        eye = objects_by_pattern([bone], 'ORG-eye')
        if deform or eye:
            yield bone


# Renames the generated rig bones to match VRoid model vertex groups.
# Bone positions are already aligned in the meta-rig.
def map_bones(conversions):
    for gen_bone, vroid_bone in conversions:
        LOGGER.info(f"renaming bone '{gen_bone.name}' to '{vroid_bone.name}'")
        gen_bone.name = vroid_bone.name
        gen_bone.use_deform = True


def adjust_finger_roll(vroid_rig, meta_rig, gen_rig):
    with editing(vroid_rig, meta_rig, gen_rig):
        edit_bones = gen_rig.data.edit_bones
        meta_edit_bones = meta_rig.data.edit_bones
        ori_edit_bones = vroid_rig.data.edit_bones
        
        META_FINGER_NAME_DIC = {
            "Thumb{}_{}": "thumb.0{}.{}",
            "Index{}_{}": "f_index.0{}.{}",
            "Middle{}_{}": "f_middle.0{}.{}",
            "Ring{}_{}": "f_ring.0{}.{}",
            "Little{}_{}": "f_pinky.0{}.{}",
        }
        
        for finger_name in FINGER_BONES:
            meta_name = META_FINGER_NAME_DIC[finger_name].format(1, "L")
            name_finger_l1 = finger_name.format(1, "L")
            name_finger_l2 = finger_name.format(2, "L")
            name_finger_l3 = finger_name.format(3, "L")
            name_finger_r1 = finger_name.format(1, "R")
            name_finger_r2 = finger_name.format(2, "R")
            name_finger_r3 = finger_name.format(3, "R")
            name_meta_finger_l1 = meta_name.format(1, "L")
            name_meta_finger_l2 = meta_name.format(2, "L")
            name_meta_finger_l3 = meta_name.format(3, "L")
            name_meta_finger_r1 = meta_name.format(1, "R")
            name_meta_finger_r2 = meta_name.format(2, "R")
            name_meta_finger_r3 = meta_name.format(3, "R")
            ori_edit_bones[name_finger_l1].roll = edit_bones[name_finger_l1].roll
            ori_edit_bones[name_finger_l2].roll = edit_bones[name_finger_l2].roll
            ori_edit_bones[name_finger_l3].roll = edit_bones[name_finger_l3].roll
            ori_edit_bones[name_finger_r1].roll = edit_bones[name_finger_r1].roll
            ori_edit_bones[name_finger_r2].roll = edit_bones[name_finger_r2].roll
            ori_edit_bones[name_finger_r3].roll = edit_bones[name_finger_r3].roll
            meta_edit_bones[name_meta_finger_l1].roll = edit_bones[name_finger_l1].roll
            meta_edit_bones[name_meta_finger_l2].roll = edit_bones[name_finger_l2].roll
            meta_edit_bones[name_meta_finger_l3].roll = edit_bones[name_finger_l3].roll
            meta_edit_bones[name_meta_finger_r1].roll = edit_bones[name_finger_r1].roll
            meta_edit_bones[name_meta_finger_r2].roll = edit_bones[name_finger_r2].roll
            meta_edit_bones[name_meta_finger_r3].roll = edit_bones[name_finger_r3].roll


# Attached bones include hair bones.
def attach_remaining_bones(vroid_rig, gen_rig):
    with editing(gen_rig, vroid_rig):
        # Assume retrieved bones are in traversal order.
        edit_bones = gen_rig.data.edit_bones
        for vroid_bone in vroid_rig.data.edit_bones:
            exists = vroid_bone.name in edit_bones
            has_parent = bool(vroid_bone.parent)
            if exists or not has_parent:
                continue

            parent_name = vroid_bone.parent.name
            can_parent = parent_name in edit_bones
            if not can_parent:
                continue

            LOGGER.info(f"generating bone '{vroid_bone.name}' as child of '{parent_name}'")
            bone = edit_bones.new(vroid_bone.name)
            bone.head = vroid_bone.head
            bone.tail = vroid_bone.tail
            bone.roll = vroid_bone.roll

            parent = edit_bones[parent_name]
            bone.layers = parent.layers
            bone.parent = parent


# Note: need to apply transforms on VRoid model
# before parenting internal meshes.
def setup_bones(vroid_rig, meta_rig, gen_rig):
    remove_gen_rig_ignored_bones(gen_rig)
    fix_gen_rig_constraint(gen_rig)
    fix_gen_rig_transfrom(vroid_rig, gen_rig)
    fix_eye(vroid_rig, gen_rig)
    base_bones = gen_rig_base_bones(gen_rig)
    map_bones(create_bone_mapping(base_bones, vroid_rig))
    adjust_finger_roll(vroid_rig, meta_rig, gen_rig)
    attach_remaining_bones(vroid_rig, gen_rig)
    LOGGER.info("amended generated rig")
