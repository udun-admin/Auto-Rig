bl_info = {
    "name": "Auto Rig",
    "author": "Carlos P",
    "version": (1,0),
    "blender": (2,93,1),
    "category": "Object",
    "location": "3D Viewport",
    "description": "Automatically rig a character for animation",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
}


if 'bpy' in locals():
    import importlib
    importlib.reload(operators)
    importlib.reload(panels)
    importlib.reload(properties)
    importlib.reload(populate)
else:
    import bpy
    from . import operators
    from . import panels
    from . import properties
    from . import populate

def register():
    operators.register()
    panels.register()
    properties.register()
    populate.register()

def unregister():
    operators.unregister()
    panels.unregister()
    properties.unregister()
    populate.unregister()