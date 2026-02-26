import bpy
import webbrowser
from mathutils import Matrix

from .presets import JIGGLE_PRESETS
from .core import RUST_AVAILABLE, update_jiggle_physics, jiggle_frame_handler


class JIGGLE_OT_manager(bpy.types.Operator):
    """Operador principal para agregar, eliminar y resetear huesos con física."""
    bl_idname = "jiggle.manager"
    bl_label = "Jiggle Manager"
    action: bpy.props.StringProperty()
    bone_name: bpy.props.StringProperty("")
    p_type: bpy.props.StringProperty("")

    def execute(self, context):
        scene = context.scene
        obj = context.object

        if not obj or obj.type != 'ARMATURE' or obj.mode != 'POSE':
            self.report({'WARNING'}, "Por favor, selecciona una Armadura y entra en Modo Pose.")
            return {'CANCELLED'}

        active_set = {n for n in scene.jiggle_active_bones.split(",") if n}

        if self.action in ["ADD_SMART", "RESET_BONE"]:
            self._add_or_reset(context, obj, active_set)
        elif self.action == "REMOVE":
            self._remove(obj, active_set)
        elif self.action == "STOP":
            self._stop_all(context, obj, active_set)

        scene.jiggle_active_bones = ",".join(sorted(list(active_set)))
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}

    def _add_or_reset(self, context, obj, active_set):
        scene = context.scene
        jiggle_col_name = "JigglePhysics"
        jiggle_col = bpy.data.collections.get(jiggle_col_name)
        if not jiggle_col:
            jiggle_col = bpy.data.collections.new(jiggle_col_name)
            scene.collection.children.link(jiggle_col)
            layer_col = context.view_layer.layer_collection.children.get(jiggle_col_name)
            if layer_col:
                layer_col.hide_viewport = True

        bones = [obj.pose.bones.get(self.bone_name)] if self.bone_name else context.selected_pose_bones
        if not bones:
            self.report({'WARNING'}, "Selecciona al menos un hueso.")
            return

        for pb in bones:
            if not pb:
                continue

            chosen = self.p_type if self.p_type else 'BREASTS'
            if self.action in ["ADD_SMART", "RESET_BONE"]:
                for p_n, p_d in JIGGLE_PRESETS.items():
                    if any(k in pb.name.lower() for k in p_d['keys']):
                        chosen = p_n
                        break
            conf = JIGGLE_PRESETS[chosen]

            # Configuración de propiedades del hueso
            pb["j_stiff"] = conf['stiff']
            pb["j_damp"] = conf['damp']
            pb["j_gravity"] = conf.get('gravity', 0.05)

            pb.id_properties_ui("j_stiff").update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
            pb.id_properties_ui("j_damp").update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
            pb.id_properties_ui("j_gravity").update(min=-1.0, max=1.0, soft_min=-1.0, soft_max=1.0)

            pb["j_vel"] = [0.0, 0.0, 0.0]

            bone_tail = obj.matrix_world @ pb.tail
            parent_name = pb.parent.name if pb.parent else ""

            # Empty: Spring
            spring_name = pb.name + "_j_spring"
            emp_spring = bpy.data.objects.get(spring_name)
            if not emp_spring:
                emp_spring = bpy.data.objects.new(spring_name, None)
                jiggle_col.objects.link(emp_spring)
            emp_spring.empty_display_size = 0.05
            emp_spring.empty_display_type = 'SPHERE'
            emp_spring.location = bone_tail
            emp_spring.hide_select = True

            # Empty: Rest
            rest_name = pb.name + "_j_rest"
            emp_rest = bpy.data.objects.get(rest_name)
            if not emp_rest:
                emp_rest = bpy.data.objects.new(rest_name, None)
                jiggle_col.objects.link(emp_rest)
            emp_rest.empty_display_size = 0.05
            emp_rest.empty_display_type = 'PLAIN_AXES'
            emp_rest.parent = obj
            emp_rest.parent_type = 'BONE' if parent_name else 'OBJECT'
            if parent_name:
                emp_rest.parent_bone = parent_name
            emp_rest.matrix_world = Matrix.Translation(bone_tail)
            emp_rest.hide_select = True

            # Constraint
            cns = pb.constraints.get("Jiggle_Track")
            if not cns:
                cns = pb.constraints.new('DAMPED_TRACK')
                cns.name = "Jiggle_Track"
            cns.target = emp_spring
            active_set.add(pb.name)

    def _remove(self, obj, active_set):
        if self.bone_name in active_set:
            active_set.remove(self.bone_name)
        pb = obj.pose.bones.get(self.bone_name)
        if pb:
            cns = pb.constraints.get("Jiggle_Track")
            if cns:
                pb.constraints.remove(cns)
            for k in ["j_stiff", "j_damp", "j_gravity", "j_vel"]:
                if k in pb:
                    del pb[k]
        for postfix in ["_j_spring", "_j_rest"]:
            emp = bpy.data.objects.get(self.bone_name + postfix)
            if emp:
                bpy.data.objects.remove(emp)

    def _stop_all(self, context, obj, active_set):
        context.scene.jiggle_is_running = False
        for b_n in active_set:
            pb = obj.pose.bones.get(b_n)
            if pb:
                cns = pb.constraints.get("Jiggle_Track")
                if cns:
                    pb.constraints.remove(cns)
                for k in ["j_stiff", "j_damp", "j_gravity", "j_vel"]:
                    if k in pb:
                        del pb[k]
        active_set.clear()
        jiggle_col = bpy.data.collections.get("JigglePhysics")
        if jiggle_col:
            for ob in list(jiggle_col.objects):
                bpy.data.objects.remove(ob)
            bpy.data.collections.remove(jiggle_col)


class JIGGLE_OT_start(bpy.types.Operator):
    """Operador modal que inicia/detiene la simulación de física en tiempo real."""
    bl_idname = "jiggle.start"
    bl_label = "Toggle Physics"
    _timer = None

    def modal(self, context, event):
        if not context.scene.jiggle_is_running:
            return self.cancel(context)
        if event.type == 'TIMER':
            if getattr(context.screen, 'is_animation_playing', False) == False:
                deps = context.evaluated_depsgraph_get()
                update_jiggle_physics(context.scene, deps)
        return {'PASS_THROUGH'}

    def execute(self, context):
        scene = context.scene
        wm = context.window_manager
        if not scene.jiggle_is_running:
            if not RUST_AVAILABLE:
                self.report({'ERROR'}, "Motor Rust no encontrado. Instalación corrupta.")
                return {'CANCELLED'}
            scene.jiggle_is_running = True
            self._timer = wm.event_timer_add(0.02, window=context.window)
            wm.modal_handler_add(self)
            if jiggle_frame_handler not in bpy.app.handlers.frame_change_post:
                bpy.app.handlers.frame_change_post.append(jiggle_frame_handler)
            return {'RUNNING_MODAL'}
        else:
            scene.jiggle_is_running = False
            return {'FINISHED'}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
        if jiggle_frame_handler in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(jiggle_frame_handler)
        return {'FINISHED'}


class JIGGLE_OT_info(bpy.types.Operator):
    """Muestra créditos del Add-on."""
    bl_idname = "jiggle.info"
    bl_label = "Jiggle Credits"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Jiggle Physics v1.3 (Rust + Gravedad)", icon='SOLO_ON')
        layout.label(text="Author: Dani blender")
        layout.operator("jiggle.open_link", text="YouTube Channel", icon='URL')

    def execute(self, context):
        return context.window_manager.invoke_props_dialog(self, width=250)


class JIGGLE_OT_open_link(bpy.types.Operator):
    """Abre el canal de YouTube del autor."""
    bl_idname = "jiggle.open_link"
    bl_label = "Open YouTube"

    def execute(self, context):
        webbrowser.open("https://www.youtube.com/@daniblender")
        return {'FINISHED'}
