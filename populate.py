from math import pi
import bpy
import mathutils
import math

# List of functions intended to build the rig. They will be used in OBJECT_OT_populate_armature() (operators.py)
# IMPORTANT: operators.OBJECT_OT_populate_armature() should be able to do its job by using populate.py functions only

def enter_edit_mode(object):
    """Enters edit mode from any situation"""
    if bpy.context.mode == 'OBJECT':
        bpy.context.view_layer.objects.active = object
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = object
    object.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.view3d.snap_cursor_to_center()

def enter_pose_mode(armature):
    """Enters pose mode from any situation"""
    if bpy.context.mode == 'OBJECT':
        bpy.context.view_layer.objects.active = armature
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.view3d.snap_cursor_to_center()

def assign_selected_to_bones_layer(lay):
    """(REQUIRES BONE SELECTION) Assign selected bones to the layer of index lay"""
    if lay not in range(0,32):
        print("Layer is not in range(0,32)")
        return
    if bpy.context.mode != 'EDIT_ARMATURE':
        print("Not in Edit Armature mode")
        return
    layer = []
    for idx in range(0,32):
        layer.append(False)
    layer[lay] = True
    bpy.ops.armature.bone_layers(layers=layer)

def assign_bones_to_layers(armature, bone_names_array, lay):
    """Assign a layer to a collection of bones"""
    enter_edit_mode(armature)
    bpy.ops.armature.select_all(action='DESELECT')
    for name in bone_names_array:
        armature.data.edit_bones[name]. select = True
    assign_selected_to_bones_layer(lay)

def assign_rotation_mode(armature, bone_names_array):
    """Assign rotation mode 'XYZ' for a collection of bones"""
    enter_pose_mode(armature)
    for name in bone_names_array:
        armature.pose.bones[name].rotation_mode = 'XYZ'

def lock_bone_transforms(armature, bone_names_array, bool_array):
    """Lock transforms as defined in the nine element array bool_array (must be an 'XYZ' rotation bone)"""
    if len(bool_array) != 9:
        print("Invalid array length")
        return
    for b in bool_array:
        if type(b) is not bool:
            print("Invalid array element")
            return
    enter_pose_mode(armature)
    for name in bone_names_array:
        pose_bone = armature.pose.bones[name]
        for idx in range(0,3):
            pose_bone.lock_location[idx] = bool_array[idx]
            pose_bone.lock_rotation[idx] = bool_array[idx + 3]
            pose_bone.lock_scale[idx] = bool_array[idx + 6]

def bone_copy_rotation_constraint(armature, bone_names_array, target_bone_name, axis_bool_array, world_local):
    """Assign a Copy Rotation constraint to a collection of bones"""
    if not world_local in {'WORLD', 'LOCAL'}:
        print("Please, select \'WORLD\' or \'LOCAL\'")
        return
    if not len(axis_bool_array) == 3:
        print("Please, pass a 3 elements array in axis_bool_array")
        return
    for b in axis_bool_array:
        if not type(b) == bool:
            print("All axis_bool_array elements must be bool")
            return
    enter_pose_mode(armature)
    constraints = []
    for name in bone_names_array:
        c = armature.pose.bones[name].constraints.new('COPY_ROTATION')
        c.target = armature
        c.subtarget = target_bone_name
        c.use_x = axis_bool_array[0]
        c.use_y = axis_bool_array[1]
        c.use_z = axis_bool_array[2]
        c.target_space = world_local
        c.owner_space = world_local
        constraints.append(c)
    return constraints

def bone_copy_transforms_constraint(armature, bone_names_array, target_bone_name, world_local):
    """Assign a Copy Transforms constraint to a collection of bones"""
    if not world_local in {'WORLD', 'LOCAL'}:
        print("Please, select \'WORLD\' or \'LOCAL\'")
        return
    enter_pose_mode(armature)
    constraints = []
    for name in bone_names_array:
        c = armature.pose.bones[name].constraints.new('COPY_TRANSFORMS')
        c.target = armature
        c.subtarget = target_bone_name
        c.target_space = world_local
        constraints.append(c)
    return constraints

def bone_IK_constraint(armature, bone_names_array, target_bone_name, pole_bone_name, chain_count, pole_angle, lock_ik_axis_array):
    """Assign a Inverse Kinematics constraint to a collection of bones"""
    if not len(lock_ik_axis_array) == 3:
        print("Please, pass a 3 elements array in axis_bool_array")
        return
    for b in lock_ik_axis_array:
        if not type(b) == bool:
            print("All lock_axis_array elements must be bool")
            return
    enter_pose_mode(armature)
    constraints = []
    for name in bone_names_array:
        c = armature.pose.bones[name].constraints.new('IK')
        c.target = armature
        c.subtarget = target_bone_name
        if pole_bone_name:
            c.pole_target = armature
            c.pole_subtarget = pole_bone_name
            c.pole_angle = pole_angle
        c.chain_count = chain_count
        constraints.append(c)
        bone = armature.pose.bones[name]
        bone.lock_ik_x = lock_ik_axis_array[0]
        bone.lock_ik_y = lock_ik_axis_array[1]
        bone.lock_ik_z = lock_ik_axis_array[2]
    return constraints

def bone_child_of_constraint(armature, bone_names_array, target_bone_name, bool_array):
    """Assign a Child Of constraint to a collection of bones"""
    enter_pose_mode(armature)
    constraints = []
    for name in bone_names_array:
        c = armature.pose.bones[name].constraints.new('CHILD_OF')
        c.target = armature
        c.subtarget = target_bone_name
        c.use_location_x = bool_array[0]
        c.use_location_y = bool_array[1]
        c.use_location_z = bool_array[2]
        c.use_rotation_x = bool_array[3]
        c.use_rotation_y = bool_array[4]
        c.use_rotation_z = bool_array[5]
        c.use_scale_x = bool_array[6]
        c.use_scale_y = bool_array[7]
        c.use_scale_z = bool_array[8]
        c.set_inverse_pending = True
        constraints.append(c)
    return constraints

def bone_damped_track_constraint(armature, bone_names_array, target_bone_name, track_axis):
    """Assign a Damped Track constraint to a collection of bones"""
    if not track_axis in ['TRACK_X', 'TRACK_Y', 'TRACK_Z', 'TRACK_NEGATIVE_X', 'TRACK_NEGATIVE_Y', 'TRACK_NEGATIVE_Z']:
        print("track axis value not in [\'TRACK_X\', \'TRACK_Y\', \'TRACK_Z\', \'TRACK_NEGATIVE_X\', \'TRACK_NEGATIVE_Y\', \'TRACK_NEGATIVE_Z\']")
        return
    enter_pose_mode(armature)
    for name in bone_names_array:
        c = armature.pose.bones[name].constraints.new('DAMPED_TRACK')
        c.target = armature
        c.subtarget = target_bone_name
        c.track_axis = track_axis
        c.head_tail = 1.0

def bone_limit_rotation_constraint(armature, bone_names_array, limit_axis, x_min_max, y_min_max, z_min_max, world_local):
    """Assign a Limit Rotation constraint to a collection of bones"""
    enter_pose_mode(armature)
    for name in bone_names_array:
        c = armature.pose.bones[name].constraints.new('LIMIT_ROTATION')
        c.use_limit_x = limit_axis[0]
        c.use_limit_y = limit_axis[1]
        c.use_limit_z = limit_axis[2]
        c.min_x = x_min_max[0]
        c.max_x = x_min_max[1]
        c.min_y = y_min_max[0]
        c.max_y = y_min_max[1]
        c.min_z = z_min_max[0]
        c.max_z = z_min_max[1]
        c.owner_space = world_local

def object_child_of_constraint(armature, object, target_bone_name, bool_array):
    """Assign a Child Of constraint to an object"""
    bpy.ops.object.mode_set(mode='OBJECT')
    c = object.constraints.new('CHILD_OF')
    c.target = armature
    c.subtarget = target_bone_name
    c.use_location_x = bool_array[0]
    c.use_location_y = bool_array[1]
    c.use_location_z = bool_array[2]
    c.use_rotation_x = bool_array[3]
    c.use_rotation_y = bool_array[4]
    c.use_rotation_z = bool_array[5]
    c.use_scale_x = bool_array[6]
    c.use_scale_y = bool_array[7]
    c.use_scale_z = bool_array[8]
    c.set_inverse_pending = True

    return c

def delete_bone_constraints_and_drivers(armature, bone_names_array):
    """Delete all constraints and drivers from a collection of bones"""
    enter_pose_mode(armature)
    for name in bone_names_array:
        bone = armature.pose.bones[name]
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

def duplicate_bones(armature, bone_names_array, new_bone_names_array, lay, is_deletable):
    """Duplicate a collection of bones, assign layer and rename them. Duplicate individually if it creates indesired bones"""
    enter_edit_mode(armature)
    bpy.ops.armature.select_all(action='DESELECT')
    for name in bone_names_array:
        edit_bone = armature.data.edit_bones[name]
        if edit_bone.parent and edit_bone.use_connect:
            edit_bone.parent.select_tail = True
        if edit_bone.children:
            for child in edit_bone.children:
                if child.use_connect:
                    child.select_head = True
        edit_bone.select = True
        edit_bone.select_head = True
        edit_bone.select_tail = True
    bpy.ops.armature.duplicate()
    assign_selected_to_bones_layer(lay)
    for idx, name in enumerate(bone_names_array):
        armature.data.edit_bones[name + ".001"].deletable = is_deletable
        armature.data.edit_bones[name + ".001"].name = new_bone_names_array[idx]
    assign_rotation_mode(armature, new_bone_names_array)

    return new_bone_names_array

def parent_bones(armature, bone_names_array, parent_bone, use_connect, use_inherit_rotation, inherit_scale):
    """Parent a collection of bones to another bone"""
    enter_edit_mode(armature)
    for name in bone_names_array:
        edit_bone = armature.data.edit_bones[name]
        edit_bone.parent = armature.data.edit_bones[parent_bone]
        edit_bone.use_connect = use_connect
        edit_bone.use_inherit_rotation = use_inherit_rotation
        edit_bone.inherit_scale = inherit_scale 

def create_spline_chain(armature, spline, cuts, bone_prefix, fit_spline):
    """Creates a bone chain that is binded to a spline"""
    spline_bones = []
    enter_edit_mode(armature)
    bpy.ops.armature.bone_primitive_add(name="new bone")
    bpy.ops.armature.select_more()
    bpy.ops.armature.subdivide(number_cuts=cuts)
    current_edit_bone = armature.data.edit_bones["new bone"]
    for idx in range(0, cuts+1):
        current_edit_bone.name = bone_prefix + "0" + str(idx+1) + "_RST"
        spline_bones.append(current_edit_bone.name)
        if idx < cuts:
            current_edit_bone = current_edit_bone.children[0]
    assign_selected_to_bones_layer(23)
    bpy.ops.object.mode_set(mode='OBJECT')
    sp_constraint = armature.pose.bones[spline_bones[len(spline_bones)-1]].constraints.new('SPLINE_IK')
    sp_constraint.target, sp_constraint.chain_count = spline, cuts + 1
    sp_constraint.use_curve_radius = False
    enter_pose_mode(armature)
    bpy.ops.pose.armature_apply(selected=True)
    sp_constraint.xz_scale_mode = 'BONE_ORIGINAL'
    if fit_spline:
        sp_constraint.y_scale_mode = 'FIT_CURVE'
    else:
        sp_constraint.y_scale_mode = 'NONE'
    assign_rotation_mode(armature, spline_bones)
    lock_bone_transforms(armature, spline_bones, [True, True, True, True, True, True, True, True, True,])
    
    return spline_bones

def create_spline_hooks(armature, spline, bone_prefix):
    """Creates bones as hooks for the spline"""
    spline_hook_bones = []
    enter_edit_mode(spline)
    spline_points_positions_vec = []
    for point in spline.data.splines[0].bezier_points:
        spline_points_positions_vec.append(point.co)
    bone_length = spline.data.splines[0].calc_length()/(len(spline_points_positions_vec)*2)

    # Apparently unnecesary conversion, but it solves some bug in mathutils
    spline_points_positions = []
    for idx, vec in enumerate(spline_points_positions_vec):
        spline_points_positions.append((vec.x, vec.y, vec.z))
    
    enter_edit_mode(armature)
    for idx, pos in enumerate(spline_points_positions):
        bpy.context.scene.cursor.location = mathutils.Vector(pos)
        bone_name = bone_prefix + "0" + str(idx+1) + "_HDL"
        bpy.ops.armature.bone_primitive_add(name=bone_name)
        armature.data.edit_bones[bone_name].length = bone_length
        spline_hook_bones.append(bone_name)

    bpy.ops.armature.select_all(action='DESELECT')
    for name in spline_hook_bones:
        edit_bone = armature.data.edit_bones[name]
        edit_bone.select = True
        edit_bone.select_head = True
        edit_bone.select_tail = True
    assign_selected_to_bones_layer(16)
    assign_rotation_mode(armature, spline_hook_bones)
    lock_bone_transforms(armature, spline_hook_bones, [False, False, False, False, False, False, True, True, True,])
    for name in spline_hook_bones:
        h_modifier = spline.modifiers.new(name, 'HOOK')
        h_modifier.object = armature
        h_modifier.subtarget = name
    enter_edit_mode(spline)
    for idx, point in enumerate(spline.data.splines[0].bezier_points):
        bpy.ops.curve.select_all(action='DESELECT')
        point.select_control_point = True
        point.select_left_handle = True
        point.select_right_handle = True
        bpy.ops.object.hook_assign(modifier=spline_hook_bones[idx])


    return spline_hook_bones

def chain_torsion(armature, result_bone_array, bone0_name, bone1_name):
    """Apply torsion to bones in a chain based on the torsion of the extremes"""
    enter_pose_mode(armature)
    for idx, name in enumerate(result_bone_array):
        dr = armature.driver_add("pose.bones[\"" + name + "\"].rotation_euler",1)
        var = dr.driver.variables.new()                                     
        var_001 = dr.driver.variables.new()
        var.type = 'TRANSFORMS'
        var_001.type = 'TRANSFORMS'
        var.targets[0].id = armature.id_data
        var_001.targets[0].id = armature.id_data
        var.targets[0].bone_target = bone0_name                             
        var_001.targets[0].bone_target = bone1_name
        var.targets[0].transform_type = 'ROT_Y'    
        var_001.targets[0].transform_type = 'ROT_Y'
        var.targets[0].transform_space = 'LOCAL_SPACE'
        var_001.targets[0].transform_space = 'LOCAL_SPACE'
        divider = len(result_bone_array) - 1
        if idx == 0:
            dr.driver.expression = "var"
        else:
            dr.driver.expression = "-1/" + str(divider) + "*var + 1/" + str(divider) + "*var_001"

def connect_tail_head(armature, tail_bone_name, head_bone_name, new_bone_name, lay, is_deletable):
    """Crate a bone that connects one bone tail to another bone head"""
    enter_edit_mode(armature)
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.context.scene.cursor.location = armature.data.edit_bones[tail_bone_name].tail
    bpy.ops.armature.bone_primitive_add(name=new_bone_name)
    bpy.ops.armature.select_more()
    assign_selected_to_bones_layer(lay)
    new_bone = armature.data.edit_bones[new_bone_name]
    new_bone.tail = armature.data.edit_bones[head_bone_name].head
    new_bone.deletable = is_deletable
    parent_bones(armature, [new_bone_name], tail_bone_name, True, True, 'FULL')
    parent_bones(armature, [head_bone_name], new_bone_name, True, True, 'FULL')
    assign_rotation_mode(armature, [new_bone_name])
    lock_bone_transforms(armature, [new_bone_name], [True, True, True, True, True, True, True, True, True])

def add_bone_axis(armature, new_bone_name, ref_bone_name, parent_name, head_tail, axis, length, use_connect, lay, is_deletable):
    """Create a bone in one axis direction"""
    enter_edit_mode(armature)
    bpy.ops.armature.select_all(action='DESELECT')
    if not head_tail in {'HEAD', 'TAIL'}:
        print("Please, select \'HEAD\' or \'TAIL\'")
        return
    if not axis in {'+X', '+Y', '+Z', '-X', '-Y', '-Z'}:
        print("Please, select \'+X\', \'+Y\', \'+Z\', \'-X\', \'-Y\' or \'-Z\'")
        return
    if head_tail == 'HEAD':
        position = armature.data.edit_bones[ref_bone_name].head
    elif head_tail == 'TAIL':
        position = armature.data.edit_bones[ref_bone_name].tail
    bpy.context.scene.cursor.location = position
    bpy.ops.armature.bone_primitive_add(name=new_bone_name)
    bpy.ops.armature.select_more()
    assign_selected_to_bones_layer(lay)
    new_bone = armature.data.edit_bones[new_bone_name]
    if axis == '+X':
        new_bone.tail.x = new_bone.head.x + length
        new_bone.tail.y = new_bone.head.y
        new_bone.tail.z = new_bone.head.z
    if axis == '+Y':
        new_bone.tail.x = new_bone.head.x
        new_bone.tail.y = new_bone.head.y + length
        new_bone.tail.z = new_bone.head.z
    if axis == '+Z':
        new_bone.tail.x = new_bone.head.x
        new_bone.tail.y = new_bone.head.y
        new_bone.tail.z = new_bone.head.z + length
    if axis == '-X':
        new_bone.tail.x = new_bone.head.x - length
        new_bone.tail.y = new_bone.head.y
        new_bone.tail.z = new_bone.head.z
    if axis == '-Y':
        new_bone.tail.x = new_bone.head.x
        new_bone.tail.y = new_bone.head.y - length
        new_bone.tail.z = new_bone.head.z
    if axis == '-Z':
        new_bone.tail.x = new_bone.head.x
        new_bone.tail.y = new_bone.head.y
        new_bone.tail.z = new_bone.head.z - length
    new_bone.deletable = is_deletable
    parent_bones(armature, [new_bone_name], parent_name, use_connect, True, 'FULL')
    assign_rotation_mode(armature, [new_bone_name])

def bone_add_hide_driver(armature, bone_name, switch_property_name, expression):
    """Add a driver to the Hide property of a bone"""
    enter_pose_mode(armature)
    dp = "bones[\"" + bone_name + "\"].hide"
    dr = armature.data.driver_add(dp)
    var = dr.driver.variables.new()
    var.targets[0].id = armature.id_data
    var.targets[0].data_path = switch_property_name
    dr.driver.expression = expression

def bone_create_fk_ik_switch(armature, result_bone, fk_bone, ik_bone, switch_property_name):
    """Creates constraints and drivers to make a result bone follow either an fk or ik bone. Creates hide drivers for fk and ik bones"""
    bone_copy_transforms_constraint(armature, [result_bone], fk_bone, 'WORLD')
    bone_copy_transforms_constraint(armature, [result_bone], ik_bone, 'WORLD')
    # Data_Path to the constraint's influence property
    dp_fk = "pose.bones[\"" + result_bone + "\"].constraints[\"Copy Transforms\"].influence"
    dp_ik = "pose.bones[\"" + result_bone + "\"].constraints[\"Copy Transforms.001\"].influence"
    # Drivers of each constraints
    dr_fk = armature.driver_add(dp_fk)
    dr_ik = armature.driver_add(dp_ik)
    # Variables of each driver
    var_fk = dr_fk.driver.variables.new()
    var_ik = dr_ik.driver.variables.new()
    # Targets of each variable
    var_fk.targets[0].id = armature.id_data
    var_ik.targets[0].id = armature.id_data
    # Paths of each target
    var_fk.targets[0].data_path = switch_property_name
    var_ik.targets[0].data_path = switch_property_name
    # Expressions of each driver
    dr_fk.driver.expression = "1-var"
    dr_ik.driver.expression = "var"

    # Driver fk_bone Hide property
    bone_add_hide_driver(armature, fk_bone, switch_property_name, "var")

    # Driver ik_bone Hide property
    bone_add_hide_driver(armature, ik_bone, switch_property_name, "1-var")

def create_fk_ik_limb(
    armature,
    bone_names_array, # Ordered as: root, second, third
    fk_names_array, # Ordered as: root, second, third
    ik_names_array, # Ordered as: root, second, third
    center_bone_name,
    pole_bone_name,
    switch_property_name,
    pole_angle,
    lock_ik_axis_array,
    handle_layer,
    aux_layer
    ):
    """Create a switchable FK IK limb (arms and legs)"""
    duplicate_bones(armature, bone_names_array, fk_names_array, handle_layer, True)
    duplicate_bones(armature, bone_names_array, ik_names_array, handle_layer, True)
    assign_bones_to_layers(armature, [ik_names_array[1]], aux_layer)
    armature.data.edit_bones[ik_names_array[2]].use_connect = False
    parent_bones(armature, [ik_names_array[2]], center_bone_name, False, True, 'FULL')
    assign_rotation_mode(armature, bone_names_array)
    lock_bone_transforms(armature, bone_names_array, [True, True, True, True, True, True, True, True, True])
    lock_bone_transforms(armature, [pole_bone_name], [False, False, False, True, True, True, True, True, True])
    lock_bone_transforms(armature, [fk_names_array[0], fk_names_array[2]], [True, True, True, False, False, False, True, True, True])
    lock_bone_transforms(armature, [fk_names_array[1]], [True, True, True, False, True, True, True, True, True])
    lock_bone_transforms(armature, [ik_names_array[0]], [True, True, True, True, True, True, False, False, False])
    lock_bone_transforms(armature, [ik_names_array[1]], [True, True, True, True, True, True, True, True, True])
    lock_bone_transforms(armature, [ik_names_array[2]], [False, False, False, False, False, False, True, True, True])
    bone_child_of_constraint(armature, [fk_names_array[0], ik_names_array[0]], center_bone_name, [False, False, False, True, True, True, False, False, False])
    bone_IK_constraint(armature, [ik_names_array[1]], ik_names_array[2], pole_bone_name, 2, pole_angle, lock_ik_axis_array)
    for idx, name in enumerate(bone_names_array):
        bone_create_fk_ik_switch(armature, name, fk_names_array[idx], ik_names_array[idx], switch_property_name)
    bone_add_hide_driver(armature, pole_bone_name, switch_property_name, "1-var")        
    
def create_forarm_torsion_bones(armature, forearm_hand_array, cuts, result_layer, aux_layer):
    """Creates the necessary bones to obtain wirst-forearm torsion"""
    new_forearm_name = forearm_hand_array[0][:-4] + "_part" + "_RST"
    new_hand_name = forearm_hand_array[1][:-4] + "_torsion" + "_AUX"
    duplicate_bones(armature, forearm_hand_array, [new_forearm_name, new_hand_name], aux_layer, True)
    delete_bone_constraints_and_drivers(armature, [new_forearm_name, new_hand_name])
    assign_bones_to_layers(armature, [new_forearm_name], result_layer)
    parent_bones(armature, [new_forearm_name, new_hand_name], forearm_hand_array[0], False, True, 'FULL')
    enter_edit_mode(armature)
    bpy.ops.armature.select_all(action='DESELECT')
    armature.data.edit_bones[new_forearm_name].select = True
    bpy.ops.armature.subdivide(number_cuts=cuts)
    forearm_parts = []
    current_edit_bone = armature.data.edit_bones[new_forearm_name]
    name = current_edit_bone.name
    for idx in range(0, cuts+1):
        current_edit_bone.name = name[:-4] + str(idx+1) + name[-4:]
        forearm_parts.append(current_edit_bone.name)
        if idx < cuts:
            current_edit_bone = current_edit_bone.children[0]
    assign_rotation_mode(armature, forearm_parts)
    lock_bone_transforms(armature,forearm_parts,[True, True, True, True, True, True, True, True, True])
    name = duplicate_bones(armature, [new_hand_name], [new_hand_name[:-4] + "_D_AUX"], aux_layer, True)[0]
    enter_edit_mode(armature)
    bpy.ops.armature.select_all(action='DESELECT')
    armature.data.edit_bones[name].select = True
    bpy.ops.armature.subdivide(number_cuts=1)
    armature.data.edit_bones[name].children[0].name = name[:-6] + "_E_AUX"
    assign_rotation_mode(armature, [name[:-6] + "_E_AUX"])
    lock_bone_transforms(armature,[name[:-6] + "_E_AUX"],[True, True, True, True, True, True, True, True, True])
    bone_damped_track_constraint(armature, [name], forearm_hand_array[1], 'TRACK_Y')
    bone_copy_rotation_constraint(armature, [name[:-6] + "_E_AUX"], forearm_hand_array[1], [True, True, True], 'WORLD')
    bone_copy_rotation_constraint(armature, [new_hand_name], name[:-6] + "_E_AUX", [True, True, True], 'LOCAL')
    chain_torsion(armature, forearm_parts, forearm_hand_array[0], new_hand_name)
    
def finger_drivers_and_constraints(armature, finger_names_array, bend_multiplier):
    """Configure all the drivers for one finger (non-thumb)"""
    enter_pose_mode(armature)
    assign_rotation_mode(armature, finger_names_array[0:3])
    lock_bone_transforms(armature, finger_names_array[0:3], [True, True, True, True, True, True, True, True, True])
    dp1 = "pose.bones[\"" + finger_names_array[1] + "\"].rotation_euler"
    dp2 = "pose.bones[\"" + finger_names_array[2] + "\"].rotation_euler"
    dr1 = armature.driver_add(dp1, 0)
    dr2 = armature.driver_add(dp2, 0)
    var1 = dr1.driver.variables.new()
    var2 = dr2.driver.variables.new()
    var1.type = 'TRANSFORMS'
    var2.type = 'TRANSFORMS'
    var1.targets[0].id = armature.id_data
    var2.targets[0].id = armature.id_data
    var1.targets[0].bone_target = finger_names_array[0]
    var2.targets[0].bone_target = finger_names_array[0]
    var1.targets[0].transform_type = 'ROT_X'
    var2.targets[0].transform_type = 'ROT_X'
    var1.targets[0].transform_space = 'LOCAL_SPACE'
    var2.targets[0].transform_space = 'LOCAL_SPACE'
    dr1.driver.expression = str(bend_multiplier) + "*1.5*var"
    dr2.driver.expression = str(bend_multiplier) + "*2.0*var"
    dp01 = "pose.bones[\"" + finger_names_array[0] + "\"].rotation_euler"
    dr01 = armature.driver_add(dp01, 2)
    var01 = dr01.driver.variables.new()
    var01.type = 'TRANSFORMS'
    var01.targets[0].id = armature.id_data
    var01.targets[0].bone_target = finger_names_array[3]
    var01.targets[0].transform_type = 'ROT_Z'
    var01.targets[0].transform_space = 'LOCAL_SPACE'
    dr01.driver.expression = "var"
    dp02 = "pose.bones[\"" + finger_names_array[0] + "\"].rotation_euler"
    dr02 = armature.driver_add(dp02, 0)
    var02 = dr02.driver.variables.new()
    var02.type = 'TRANSFORMS'
    var02.targets[0].id = armature.id_data
    var02.targets[0].bone_target = finger_names_array[3]
    var02.targets[0].transform_type = 'SCALE_AVG'
    var02.targets[0].transform_space = 'LOCAL_SPACE'
    dr02.driver.expression = "-var + 1"

def thumb_drivers_and_constraints(armature, finger_names_array, bend_multiplier):
    """Configure all the drivers for one thumb"""
    enter_pose_mode(armature)
    assign_rotation_mode(armature, finger_names_array[0:3])
    lock_bone_transforms(armature, finger_names_array[0:3], [True, True, True, True, True, True, True, True, True])
    dp2 = "pose.bones[\"" + finger_names_array[2] + "\"].rotation_euler"
    dr2 = armature.driver_add(dp2, 0)
    var2 = dr2.driver.variables.new()
    var2.type = 'TRANSFORMS'
    var2.targets[0].id = armature.id_data
    var2.targets[0].bone_target = finger_names_array[1]
    var2.targets[0].transform_type = 'ROT_X'
    var2.targets[0].transform_space = 'LOCAL_SPACE'
    dr2.driver.expression = str(bend_multiplier) + "*2.0*var"
    dp11 = "pose.bones[\"" + finger_names_array[1] + "\"].rotation_euler"
    dr11 = armature.driver_add(dp11, 2)
    var11 = dr11.driver.variables.new()
    var11.type = 'TRANSFORMS'
    var11.targets[0].id = armature.id_data
    var11.targets[0].bone_target = finger_names_array[4]
    var11.targets[0].transform_type = 'ROT_Z'
    var11.targets[0].transform_space = 'LOCAL_SPACE'
    dr11.driver.expression = "var"
    dp12 = "pose.bones[\"" + finger_names_array[1] + "\"].rotation_euler"
    dr12 = armature.driver_add(dp12, 0)
    var12 = dr12.driver.variables.new()
    var12.type = 'TRANSFORMS'
    var12.targets[0].id = armature.id_data
    var12.targets[0].bone_target = finger_names_array[4]
    var12.targets[0].transform_type = 'SCALE_AVG'
    var12.targets[0].transform_space = 'LOCAL_SPACE'
    dr12.driver.expression = "-var + 1"
    bone_copy_rotation_constraint(armature, [finger_names_array[0]], finger_names_array[3], [True, True, True], 'WORLD')

def create_heel_foot_control(armature, mch_names_array, ik_main_name, switch_property_name, aux_layer, handle_layer):
    """Create the foot-heel mechanism"""
    enter_edit_mode(armature)
    length = armature.data.edit_bones[mch_names_array[1]].length
    # Create roll bone
    roll_name = mch_names_array[1][:-8] + "_roll_HDL"
    add_bone_axis(armature, roll_name, mch_names_array[0], ik_main_name, 'HEAD', '-Y', length, False, handle_layer, True)
    lock_bone_transforms(armature, [roll_name], [True, True, True, False, True, False, True, True, True])
    bone_add_hide_driver(armature, roll_name, switch_property_name, "1-var")
    # Create heel bone
    heel_name = mch_names_array[1][:-8] + "_heel_AUX"
    add_bone_axis(armature, heel_name, ik_main_name, ik_main_name, 'TAIL', '-Y', length, False, aux_layer, True)
    lock_bone_transforms(armature, [heel_name], [True, True, True, True, True, True, True, True, True])
    # Create pivot bone
    pivot_name = mch_names_array[1][:-8] + "_pivot_HDL"
    add_bone_axis(armature, pivot_name, mch_names_array[1], heel_name, 'HEAD', '-Y', length, False, aux_layer, True)
    lock_bone_transforms(armature, [pivot_name], [True, True, True, True, True, True, True, True, True])

    # Parent mch bones
    parent_bones(armature, [mch_names_array[0]], pivot_name, False, True, 'FULL')
    parent_bones(armature, [mch_names_array[1]], heel_name, False, True, 'FULL')

    # Pivot bone constraints
    bone_copy_rotation_constraint(armature, [pivot_name], roll_name, [True, True, True], 'LOCAL')
    bone_limit_rotation_constraint(armature, [pivot_name], [True, False, False], [0.0, math.radians(170)], [0.0,0.0], [0.0,0.0], 'LOCAL')
    
    # Heel bone constraints
    bone_copy_rotation_constraint(armature, [heel_name], roll_name, [True, False, False], 'LOCAL')
    bone_limit_rotation_constraint(armature, [heel_name], [True, False, False], [math.radians(-170),0.0], [0.0,0.0], [0.0,0.0], 'LOCAL')

    bone_add_hide_driver(armature, ik_main_name, switch_property_name, "1-var")





def register():
    pass

def unregister():
    pass