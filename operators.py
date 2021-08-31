import bpy
import os
from . import populate
import math

class OBJECT_OT_add_source_armature(bpy.types.Operator):
    bl_idname = 'object.add_source_armature'
    bl_label = 'Add Armature'

    def execute(self, context):
        scene = context.scene
        path = os.path.dirname(__file__) + '/source armature.blend\\Collection'
        collection_name = 'Armature Collection'
        bpy.ops.wm.append(
            directory=path,
            filename=collection_name
        )
        for ob in context.selectable_objects:
            if ob.production_state == 'TEMPLATE':
                ob.production_state = 'BASIC_EDITION'
                scene.armature_ob = ob.id_data
                break
        return {'FINISHED'}

class OBJECT_OT_clean_armature(bpy.types.Operator):
    """Return the armature back to the template state"""
    bl_idname = 'object.clean_armature'
    bl_label = 'Clean'

    def execute(self, context):
        if not bpy.context.scene.armature_ob:
            return {'FINISHED'}
        try:
            armature = bpy.context.scene.armature_ob
        except KeyError:
            return {'FINISHED'}
        coll = armature.users_collection[0]
        # Create spline dictionary
        splines = {}
        for ob in coll.objects:
            if not ob.type == 'CURVE':
                continue
            splines[ob.name] = ob
        
        # Clean armature
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            return {'FINISHED'}
        for bone in armature.pose.bones:
            for c in bone.constraints:
                bone.constraints.remove(c)
            paths = []
            paths.append('pose.bones[\"' + bone.name + '\"].location')
            paths.append('pose.bones[\"' + bone.name + '\"].rotation_euler')
            paths.append('pose.bones[\"' + bone.name + '\"].rotation_quaternion')
            paths.append('pose.bones[\"' + bone.name + '\"].scale')
            paths.append('pose.bones[\"' + bone.name + '\"].constraints[\"' + 'Copy Transforms' + '\"].influence')
            paths.append('pose.bones[\"' + bone.name + '\"].constraints[\"' + 'Copy Transforms.001' + '\"].influence')
            for p in paths:
                armature.driver_remove(p)
            armature.data.driver_remove('bones[\"' + bone.name + '\"].hide')
        
        # Delete deletable bones
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        for edit_bone in armature.data.edit_bones:
            if not edit_bone.deletable:
                continue
            armature.data.edit_bones.remove(edit_bone)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Clean splines
        for name, spline in splines.items():
            for c in spline.constraints:
                spline.constraints.remove(c)
            for m in spline.modifiers:
                spline.modifiers.remove(m)
        
        return {'FINISHED'}

class OBJECT_OT_delete_armature(bpy.types.Operator):
    """Delete the current armature"""
    bl_idname = 'object.delete_armature'
    bl_label = 'Delete'

    def execute(self, context):
        if not bpy.context.scene.armature_ob:
            return {'FINISHED'}

        try:
            armature = bpy.context.scene.armature_ob
        except KeyError:
            return {'FINISHED'}

        coll = armature.users_collection[0]

        for ob in coll.objects:
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(coll, do_unlink=True)
        
        return {'FINISHED'}

class OBJECT_OT_populate_armature(bpy.types.Operator):
    """Populate the template armature to make it animation ready"""
    bl_idname = 'object.populate_armature'
    bl_label = 'Populate armature'
    def execute(self, context):
        # Try to get the armature
        if not bpy.context.scene.armature_ob:
            return {'FINISHED'}

        try:
            armature = bpy.context.scene.armature_ob
        except KeyError:
            return {'FINISHED'}

        # Splines dictionary
        splines = {}
        for name, ob in bpy.data.objects.items():
            if not name.endswith("_SPL"):
                continue
            splines[name] = ob

        # Populate operations
        # IMPORTANT: It is highly recommended to use populate functions only!
        # Spine
        spine_RST_bones = populate.create_spline_chain(armature, splines["spine_SPL"], 6, "spine", False)
        spine_HDL_bones = populate.create_spline_hooks(armature, splines["spine_SPL"], "spine")
        populate.chain_torsion(
            armature, 
            spine_RST_bones, 
            armature.pose.bones[spine_HDL_bones[0]].name,
            armature.pose.bones[spine_HDL_bones[len(spine_HDL_bones)-1]].name
        )
        populate.duplicate_bones(armature, [spine_HDL_bones[0]], ["hips_location_HDL"], 16, True)
        populate.parent_bones(armature, spine_HDL_bones, "hips_location_HDL", False, True, 'FULL')
        populate.parent_bones(armature, ["hips_location_HDL"], "center_HDL", False, True, 'FULL')
        populate.parent_bones(armature, [spine_RST_bones[0]], "center_HDL", False, False, 'FULL')
        populate.bone_child_of_constraint(armature, [spine_RST_bones[0]], spine_HDL_bones[0], [True, True, True, True, True, True, False, False, False])
        populate.object_child_of_constraint(armature, splines["spine_SPL"], spine_HDL_bones[0], [True, True, True, True, True, True, True, True, True])
        populate.lock_bone_transforms(armature, ["hips_location_HDL"], [False, False, False, True, True, True, True, True, True])
        populate.lock_bone_transforms(armature, [spine_HDL_bones[0]], [True, True, True, False, False, False, True, True, True])
        populate.lock_bone_transforms(armature, [spine_HDL_bones[len(spine_HDL_bones)-1]], [False, False, False, False, False, False, True, True, True])
        for idx in range(1,len(spine_HDL_bones)-1):
            populate.lock_bone_transforms(armature, [spine_HDL_bones[idx]], [False, False, False, False, True, False, True, True, True])
        
        # Shoulders
        populate.connect_tail_head(armature,spine_RST_bones[len(spine_RST_bones)-1], "shoulder_left_RST", "shoulder_con_left_AUX", 7, True)
        populate.connect_tail_head(armature,spine_RST_bones[len(spine_RST_bones)-1], "shoulder_right_RST", "shoulder_con_right_AUX", 7, True)
        populate.parent_bones(armature, ["shoulder_left_RST"], "shoulder_con_left_AUX", True, False, 'FULL')
        populate.parent_bones(armature, ["shoulder_right_RST"], "shoulder_con_right_AUX", True, False, 'FULL')
        populate.add_bone_axis(armature, "shoulder_left_HDL", "shoulder_left_RST", "shoulder_con_left_AUX", 'HEAD', '-X', 0.3, True, 16, True)
        populate.add_bone_axis(armature, "shoulder_right_HDL", "shoulder_right_RST", "shoulder_con_right_AUX", 'HEAD', '+X', 0.3, True, 16, True)
        populate.assign_rotation_mode(armature, ["shoulder_left_RST", "shoulder_right_RST"])
        populate.lock_bone_transforms(armature, ["shoulder_left_RST", "shoulder_right_RST"], [True, True, True, True, True, True, True, True, True])
        populate.lock_bone_transforms(armature, ["shoulder_left_HDL", "shoulder_right_HDL"], [True, True, True, False, False, False, True, True, True])
        populate.bone_child_of_constraint(armature, ["shoulder_left_RST"], "shoulder_left_HDL", [False, False, False, True, True, True, False, False, False])
        populate.bone_child_of_constraint(armature, ["shoulder_right_RST"], "shoulder_right_HDL", [False, False, False, True, True, True, False, False, False])

        # Neck-Head
        populate.connect_tail_head(armature, spine_RST_bones[len(spine_RST_bones)-1], "neck01_RST", "neck_con_AUX", 7, True)
        populate.assign_rotation_mode(armature,["neck01_RST", "neck02_RST", "head_RST"])
        populate.duplicate_bones(armature, ["neck01_RST"], ["neck_HDL"], 16, True)
        populate.duplicate_bones(armature, ["head_RST"], ["head_HDL"], 16, True)
        populate.lock_bone_transforms(armature, ["neck01_RST", "neck02_RST", "head_RST"], [True, True, True, True, True, True, True, True, True])
        populate.parent_bones(armature, ["neck_HDL"], "neck_con_AUX", True, False, 'FULL')
        populate.parent_bones(armature, ["head_HDL"], "neck_HDL", False, False, 'FULL')
        populate.lock_bone_transforms(armature, ["neck_HDL", "head_HDL"], [False, False, False, False, False, False, True, True, True])
        populate.bone_copy_rotation_constraint(armature, ["neck01_RST"], "neck_HDL", [True, True, True], 'WORLD')
        populate.bone_child_of_constraint(armature, ["neck_HDL", "head_HDL"], "center_HDL", [False, False, False, True, True, True, False, False, False])
        populate.bone_IK_constraint(armature, ["neck02_RST"], "head_HDL", None, 1, 0.0, [False, False, False])
        populate.bone_copy_transforms_constraint(armature, ["head_RST"], "head_HDL", 'WORLD')

        # Arms
        populate.create_fk_ik_limb(
            armature,
            ["arm_left_RST", "forearm_left_AUX", "hand_left_RST"], # Ordered as: root, second, third, pole
            ["arm_left_fk_HDL", "forearm_left_fk_HDL", "hand_left_fk_HDL"], # Ordered as: root, first, second
            ["arm_left_ik_HDL", "forearm_left_ik_AUX", "hand_left_ik_HDL"], # Ordered as: root, first, second
            "center_HDL",
            "arm_left_Pole_HDL",
            "fk_ik_left_arm",
            math.radians(0),
            [False, False, True],
            16,
            7
            )
        populate.create_fk_ik_limb(
            armature,
            ["arm_right_RST", "forearm_right_AUX", "hand_right_RST"], # Ordered as: root, second, third, pole
            ["arm_right_fk_HDL", "forearm_right_fk_HDL", "hand_right_fk_HDL"], # Ordered as: root, first, second
            ["arm_right_ik_HDL", "forearm_right_ik_AUX", "hand_right_ik_HDL"], # Ordered as: root, first, second
            "center_HDL",
            "arm_right_Pole_HDL",
            "fk_ik_right_arm",
            math.radians(180),
            [False, False, True],
            16,
            7
            )
        populate.create_forarm_torsion_bones(armature, ["forearm_left_AUX", "hand_left_RST"], 3, 23, 7)
        populate.create_forarm_torsion_bones(armature, ["forearm_right_AUX", "hand_right_RST"], 3, 23, 7)

        # Hands
        populate.finger_drivers_and_constraints(armature, ["index_01_left_RST", "index_02_left_RST", "index_03_left_RST", "index_left_HDL"], 1.0)
        populate.finger_drivers_and_constraints(armature, ["middle_01_left_RST", "middle_02_left_RST", "middle_03_left_RST", "middle_left_HDL"], 1.0)
        populate.finger_drivers_and_constraints(armature, ["ring_01_left_RST", "ring_02_left_RST", "ring_03_left_RST", "ring_left_HDL"], 1.0)
        populate.finger_drivers_and_constraints(armature, ["pinky_01_left_RST", "pinky_02_left_RST", "pinky_03_left_RST", "pinky_left_HDL"], 1.0)
        populate.thumb_drivers_and_constraints(armature, ["thumb_01_left_RST", "thumb_02_left_RST", "thumb_03_left_RST", "thumb_root_left_HDL", "thumb_left_HDL"], 1.0)
        
        populate.finger_drivers_and_constraints(armature, ["index_01_right_RST", "index_02_right_RST", "index_03_right_RST", "index_right_HDL"], 1.0)
        populate.finger_drivers_and_constraints(armature, ["middle_01_right_RST", "middle_02_right_RST", "middle_03_right_RST", "middle_right_HDL"], 1.0)
        populate.finger_drivers_and_constraints(armature, ["ring_01_right_RST", "ring_02_right_RST", "ring_03_right_RST", "ring_right_HDL"], 1.0)
        populate.finger_drivers_and_constraints(armature, ["pinky_01_right_RST", "pinky_02_right_RST", "pinky_03_right_RST", "pinky_right_HDL"], 1.0)
        populate.thumb_drivers_and_constraints(armature, ["thumb_01_right_RST", "thumb_02_right_RST", "thumb_03_right_RST", "thumb_root_right_HDL", "thumb_right_HDL"], 1.0)

        # Legs
        # Left
        populate.create_fk_ik_limb(
            armature,
            ["thigh_left_RST", "calf_left_RST", "foot_left_RST"], # Ordered as: root, second, third, pole
            ["thigh_left_fk_HDL", "calf_left_fk_HDL", "foot_left_fk_HDL"], # Ordered as: root, first, second
            ["thigh_left_ik_HDL", "calf_left_ik_AUX", "foot_left_mech_AUX"], # Ordered as: root, first, second
            "center_HDL",
            "leg_left_Pole_HDL",
            "fk_ik_left_leg",
            math.radians(90),
            [False, True, True],
            16,
            7
            )
        populate.parent_bones(armature, ["thigh_left_fk_HDL", "thigh_left_ik_HDL"], spine_RST_bones[0], False, False, 'FULL')
        
        # Right
        populate.create_fk_ik_limb(
            armature,
            ["thigh_right_RST", "calf_right_RST", "foot_right_RST"], # Ordered as: root, second, third, pole
            ["thigh_right_fk_HDL", "calf_right_fk_HDL", "foot_right_fk_HDL"], # Ordered as: root, first, second
            ["thigh_right_ik_HDL", "calf_right_ik_AUX", "foot_right_mech_AUX"], # Ordered as: root, first, second
            "center_HDL",
            "leg_right_Pole_HDL",
            "fk_ik_right_leg",
            math.radians(90),
            [False, True, True],
            16,
            7
            )
        populate.parent_bones(armature, ["thigh_right_fk_HDL", "thigh_right_ik_HDL"], spine_RST_bones[0], False, False, 'FULL')


        # Feet
        # Left
        populate.assign_bones_to_layers(armature, ["foot_left_mech_AUX"], 7)
        populate.assign_rotation_mode(armature, ["toe_left_RST"])
        populate.duplicate_bones(armature, ["toe_left_RST"], ["toe_left_fk_HDL"], 16, True)
        populate.duplicate_bones(armature, ["toe_left_RST"], ["toe_left_mch_AUX"], 7, True)
        populate.lock_bone_transforms(armature, ["toe_left_RST"], [True, True, True, True, True, True, True, True, True])
        populate.lock_bone_transforms(armature, ["toe_left_fk_HDL"], [True, True, True, False, False, False, True, True, True])
        populate.lock_bone_transforms(armature, ["toe_left_mch_AUX"], [True, True, True, True, True, True, True, True, True])
        populate.parent_bones(armature, ["toe_left_fk_HDL"], "foot_left_fk_HDL", True, True, 'FULL')
        populate.bone_create_fk_ik_switch(armature, "toe_left_RST", "toe_left_fk_HDL", "toe_left_mch_AUX", "fk_ik_left_leg")

        populate.create_heel_foot_control(armature, ["foot_left_mech_AUX", "toe_left_mch_AUX"], "foot_left_IK_main_HDL", "fk_ik_left_leg", 7, 16)

        # Right
        populate.assign_bones_to_layers(armature, ["foot_right_mech_AUX"], 7)
        populate.assign_rotation_mode(armature, ["toe_right_RST"])
        populate.duplicate_bones(armature, ["toe_right_RST"], ["toe_right_fk_HDL"], 16, True)
        populate.duplicate_bones(armature, ["toe_right_RST"], ["toe_right_mch_AUX"], 7, True)
        populate.lock_bone_transforms(armature, ["toe_right_RST"], [True, True, True, True, True, True, True, True, True])
        populate.lock_bone_transforms(armature, ["toe_right_fk_HDL"], [True, True, True, False, False, False, True, True, True])
        populate.lock_bone_transforms(armature, ["toe_right_mch_AUX"], [True, True, True, True, True, True, True, True, True])
        populate.parent_bones(armature, ["toe_right_fk_HDL"], "foot_right_fk_HDL", True, True, 'FULL')
        populate.bone_create_fk_ik_switch(armature, "toe_right_RST", "toe_right_fk_HDL", "toe_right_mch_AUX", "fk_ik_right_leg")

        populate.create_heel_foot_control(armature, ["foot_right_mech_AUX", "toe_right_mch_AUX"], "foot_right_IK_main_HDL", "fk_ik_right_leg", 7, 16)


        return {'FINISHED'}

class MESSAGE_WM_delete_previous_popup(bpy.types.Operator):
    """Add a new armature template (delete the previous one if any)"""
    bl_idname='wm.delete_previous_popup'
    bl_label='Delete previous armature?'
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.delete_armature()
        bpy.ops.object.add_source_armature()
        return{'FINISHED'}

    def invoke(self, context, event):
        for ob in context.selectable_objects:
            if not ob.id_data is bpy.context.scene.armature_ob:
                continue
            return context.window_manager.invoke_confirm(self,event)
        bpy.ops.object.add_source_armature()
        return {'INTERFACE'}

def register():
    bpy.utils.register_class(OBJECT_OT_add_source_armature)
    bpy.utils.register_class(OBJECT_OT_clean_armature)
    bpy.utils.register_class(OBJECT_OT_delete_armature)
    bpy.utils.register_class(OBJECT_OT_populate_armature)
    bpy.utils.register_class(MESSAGE_WM_delete_previous_popup)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_source_armature)
    bpy.utils.unregister_class(OBJECT_OT_clean_armature)
    bpy.utils.unregister_class(OBJECT_OT_delete_armature)
    bpy.utils.unregister_class(OBJECT_OT_populate_armature)
    bpy.utils.unregister_class(MESSAGE_WM_delete_previous_popup)