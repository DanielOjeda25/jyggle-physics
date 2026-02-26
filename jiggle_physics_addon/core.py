import bpy
from bpy.app.handlers import persistent

# --- IMPORTAMOS NUESTRO MOTOR RUST ---
# Intentamos importación relativa (para cuando esté en formato ZIP)
# y si falla, intentamos importación local (para cuando usas el editor de texto de Blender)
try:
    from . import jiggle_rust_core
    RUST_AVAILABLE = True
    print("¡Motor Jiggle Rust cargado correctamente (Modo Add-on)!")
except ImportError:
    try:
        import jiggle_rust_core
        RUST_AVAILABLE = True
        print("¡Motor Jiggle Rust cargado correctamente (Modo Local)!")
    except ImportError:
        RUST_AVAILABLE = False
        print("ADVERTENCIA: No se encontró 'jiggle_rust_core'. Las físicas no se ejecutarán.")


def update_jiggle_physics(scene, deps):
    """Calcula la física de muelle para cada hueso activo usando el motor Rust."""
    if not RUST_AVAILABLE:
        return

    active_bones_str = scene.jiggle_active_bones
    if not active_bones_str:
        return
    active_bones = [b for b in active_bones_str.split(",") if b]

    armatures = [ob for ob in scene.objects if ob.type == 'ARMATURE']

    for obj in armatures:
        for bone_name in active_bones:
            pb = obj.pose.bones.get(bone_name)
            if not pb or "j_stiff" not in pb:
                continue

            emp_spring = bpy.data.objects.get(bone_name + "_j_spring")
            emp_rest = bpy.data.objects.get(bone_name + "_j_rest")

            if not emp_spring or not emp_rest:
                continue

            stiff = max(0.001, min(pb["j_stiff"], 1.0))
            damp = max(0.0, min(pb["j_damp"], 0.99))

            # --- Extraemos la gravedad de las propiedades del hueso ---
            gravity = float(pb.get("j_gravity", 0.05))

            emp_rest_eval = emp_rest.evaluated_get(deps)

            rest_pos_list = [
                emp_rest_eval.matrix_world.translation.x,
                emp_rest_eval.matrix_world.translation.y,
                emp_rest_eval.matrix_world.translation.z,
            ]

            spring_pos_list = [
                emp_spring.location.x,
                emp_spring.location.y,
                emp_spring.location.z,
            ]

            vel_data = pb.get("j_vel", [0.0, 0.0, 0.0])
            current_vel_list = [float(vel_data[0]), float(vel_data[1]), float(vel_data[2])]

            try:
                # --- Pasamos la gravedad a Rust ---
                new_pos, new_vel = jiggle_rust_core.calcular_fisica_frame(
                    rest_pos_list,
                    spring_pos_list,
                    current_vel_list,
                    stiff,
                    damp,
                    gravity,
                )
            except Exception as e:
                print(f"Error en el cálculo de Rust: {e}")
                continue

            emp_spring.location = new_pos
            pb["j_vel"] = new_vel


@persistent
def jiggle_frame_handler(scene):
    """Handler que se ejecuta en cada cambio de frame."""
    if not scene.jiggle_is_running:
        return
    deps = bpy.context.evaluated_depsgraph_get()
    update_jiggle_physics(scene, deps)
