import bpy

def register():
    
    bpy.types.Object.fk_ik_left_arm = bpy.props.FloatProperty(
        name='FK-IK left arm',
        description='Select FK-IK left arm',
        default=0.0,
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'},
    )
    bpy.types.Object.fk_ik_right_arm = bpy.props.FloatProperty(
        name='FK-IK right arm',
        description='Select FK-IK right arm',
        default=0.0,
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'},
    )
    bpy.types.Object.fk_ik_left_leg = bpy.props.FloatProperty(
        name='FK-IK left leg',
        description='Select FK-IK left leg',
        default=1.0,
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'},
    )
    bpy.types.Object.fk_ik_right_leg = bpy.props.FloatProperty(
        name='FK-IK right leg',
        description='Select FK-IK right leg',
        default=1.0,
        min=0.0,
        max=1.0,
        options={'ANIMATABLE'},
    )
    bpy.types.Object.production_state = bpy.props.EnumProperty(
        name='production state',
        description='production state of the armature object',
        items=[
            ('NONE', 'none', 'not an Auto Rig armature object'),
            ('TEMPLATE', 'template', 'source file'),
            ('BASIC_EDITION', 'basic edition', 'adding basic bones'),
            ('EXTRAS_EDITION', 'extras edition', 'adding extra bones'),
            ('READY', 'ready', 'ready to animate')
        ],
        default='NONE',
    )
    bpy.types.Scene.armature_ob = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name='edit armature',
        description='the armature being edited'
    )
    bpy.types.EditBone.deletable = bpy.props.BoolProperty(
        name='deletable',
        description='bone is deletable in clean_armature()',
        default=True,
    )

def unregister():
    del bpy.types.Object.fk_ik_left_arm
    del bpy.types.Object.fk_ik_right_arm
    del bpy.types.Object.fk_ik_left_leg
    del bpy.types.Object.fk_ik_right_leg
    del bpy.types.Object.production_state
    del bpy.types.Scene.armature_ob
    del bpy.types.EditBone.deletable