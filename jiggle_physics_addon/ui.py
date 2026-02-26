import bpy

from .presets import JIGGLE_PRESETS
from .core import RUST_AVAILABLE


class JIGGLE_PT_Main(bpy.types.Panel):
    """Panel principal en la barra lateral del Viewport 3D."""
    bl_label = "Jiggle Physics v1.3"
    bl_idname = "VIEW3D_PT_jiggle_v1"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Jiggle'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        # Header
        row = layout.row(align=True)
        row.label(text="by Dani blender", icon='USER')
        row.operator("jiggle.info", text="", icon='INFO')

        # Rust check
        if not RUST_AVAILABLE:
            box = layout.box()
            box.label(text="ERROR CRÍTICO:", icon='ERROR')
            box.label(text="Motor Rust no encontrado.")
            return

        layout.separator()

        # Preset buttons
        box = layout.box()
        box.label(text="Apply to Selection:", icon='RESTRICT_SELECT_OFF')
        row = box.row(align=True)
        for name, data in JIGGLE_PRESETS.items():
            op = row.operator("jiggle.manager", text=name, icon=data['icon'])
            op.action, op.p_type = "ADD_SMART", name

        # Active bones list
        if scene.jiggle_active_bones and obj and obj.type == 'ARMATURE':
            layout.label(text="Active Physics Bones:", icon='BONE_DATA')
            for b_name in scene.jiggle_active_bones.split(","):
                if not b_name:
                    continue
                pb = obj.pose.bones.get(b_name)
                if not pb:
                    continue
                b_box = layout.box()
                row = b_box.row(align=True)
                row.label(text=b_name)
                res = row.operator("jiggle.manager", text="", icon='FILE_REFRESH')
                res.action, res.bone_name = "RESET_BONE", b_name
                dele = row.operator("jiggle.manager", text="", icon='TRASH')
                dele.action, dele.bone_name = "REMOVE", b_name
                if "j_stiff" in pb:
                    col = b_box.column(align=True)
                    col.prop(pb, '["j_stiff"]', text="Stiffness", slider=True)
                    col.prop(pb, '["j_damp"]', text="Damping", slider=True)
                    # --- Slider de Gravedad en el panel de control ---
                    col.prop(pb, '["j_gravity"]', text="Gravity", slider=True)

        # Start / Stop controls
        layout.separator()
        col = layout.column(align=True)
        if not scene.jiggle_is_running:
            col.operator("jiggle.start", text="Start Physics", icon='PLAY')
        else:
            col.operator("jiggle.start", text="Stop Physics", icon='PAUSE')
        col.operator("jiggle.manager", text="Clear & Reset All", icon='X').action = "STOP"
