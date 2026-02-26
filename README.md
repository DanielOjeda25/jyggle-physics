# 🚀 Jiggle Physics v1.3 (Rust Powered)

Un Add-on profesional para **Blender 4.0 / 5.0** diseñado para añadir dinámicas de físicas en tiempo real (spring bones) a tus armaduras. Optimizado al máximo utilizando un motor matemático nativo escrito en **Rust**.

## ✨ Características Principales

* **Rendimiento Extremo (Rust Core):** Los cálculos matemáticos pesados se ejecutan en un binario de Rust (`.pyd`), permitiendo simulaciones a 60 FPS en el visor 3D sin ahogar tu procesador.
* **Gravedad Realista:** Incluye un vector de gravedad ajustable para que los rebotes tengan peso real, evitando el efecto de "gravedad cero".
* **Presets Inteligentes:** Configuración a un clic para `Breasts` y `Butts` con valores de rigidez (stiffness), amortiguación (damping) y gravedad (gravity) pre-calibrados.
* **Flujo de Trabajo No Destructivo:** Agrega, resetea o elimina las físicas de cualquier hueso sin romper tu rig original.

## 📥 Instalación

1. Ve a la sección de **Releases** a la derecha de esta página y descarga el archivo `jiggle_physics_addon.zip`. *(Nota: No descargues el código fuente, descarga el ZIP compilado).*
2. Abre Blender y ve a `Edit > Preferences > Add-ons`.
3. Haz clic en **Install...** y selecciona el archivo `.zip` que acabas de descargar.
4. Activa la casilla junto a **Animation: Jiggle Physics**.

*(Requisito: Actualmente el motor Rust está compilado para Windows de 64 bits).*

## 🎮 Cómo usarlo

1. Selecciona tu **Armadura** y entra en **Pose Mode**.
2. Abre el panel lateral (letra `N`) y busca la pestaña **Jiggle**.
3. Selecciona los huesos a los que quieras aplicar físicas (ej. los huesos del pecho o glúteos).
4. Haz clic en el preset deseado (Breasts / Butt) en la sección *Apply to Selection*.
5. Presiona el botón **▶️ Start Physics**.
6. ¡Mueve el control principal de tu personaje o dale Play a la línea de tiempo para ver la física en acción!

Puedes ajustar los valores de `Stiffness`, `Damping` y `Gravity` individualmente para cada hueso desde el mismo panel.

## 🛠️ Desarrollo y Compilación (Para desarrolladores)

Este proyecto utiliza `PyO3` y `maturin` para el backend en Rust. Si deseas compilarlo desde cero o para otro sistema operativo:
1. Asegúrate de tener Rust instalado.
2. Localiza el ejecutable de Python integrado en tu instalación de Blender.
3. Ejecuta: `"Ruta\A\Blender\python.exe" -m maturin build --release` dentro de la carpeta `jiggle_rust_core`.

---
*Creado por **Dani blender**. ¡Visita mi [Canal de YouTube](https://www.youtube.com/@daniblender) para tutoriales y más herramientas!*