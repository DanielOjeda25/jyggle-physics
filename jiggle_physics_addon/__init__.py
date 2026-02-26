import bpy

from .core import jiggle_frame_handler
from .operators import (
    JIGGLE_OT_manager,
    JIGGLE_OT_start,
    JIGGLE_OT_info,
    JIGGLE_OT_open_link,
)
from .ui import JIGGLE_PT_Main

bl_info = {
    "name": "Jiggle Physics",
    "author": "Dani blender",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Jiggle",
    "description": "Añade dinámicas de físicas en tiempo real (spring bones) a tus armaduras de forma profesional.",
    "doc_url": "https://www.youtube.com/@daniblender",
    "category": "Animation",
}

classes = (
    JIGGLE_OT_manager,
    JIGGLE_OT_start,
    JIGGLE_OT_info,
    JIGGLE_OT_open_link,
    JIGGLE_PT_Main,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.jiggle_active_bones = bpy.props.StringProperty(default="", maxlen=2048)
    bpy.types.Scene.jiggle_is_running = bpy.props.BoolProperty(default=False)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.jiggle_active_bones
    del bpy.types.Scene.jiggle_is_running
    if jiggle_frame_handler in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(jiggle_frame_handler)


if __name__ == "__main__":
    register()
