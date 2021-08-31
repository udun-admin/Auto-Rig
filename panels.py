import bpy

# The edit rig panel
class VIEW3D_PT_edit_rig(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Auto Rig"
    bl_label = "Create new Armature"

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        row = layout.row()
        column.operator('wm.delete_previous_popup', text='Add armature')
        column.operator('object.populate_armature')
        row.operator('object.clean_armature', icon='PANEL_CLOSE')
        row.operator('object.delete_armature', icon='CANCEL')

class OBJECT_PT_armature_options(bpy.types.Panel):
    bl_label = "Armature Options"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None) and (context.object.production_state == 'READY')

    def draw_header(self, context):
        layout = self.layout
        obj = context.object

    def draw(self, context):
        pass


def register():
    bpy.utils.register_class(VIEW3D_PT_edit_rig)
    bpy.utils.register_class(OBJECT_PT_armature_options)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_edit_rig)
    bpy.utils.unregister_class(OBJECT_PT_armature_options)