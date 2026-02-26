use pyo3::prelude::*;

#[pyfunction]
fn calcular_fisica_frame(
    rest_pos: [f32; 3],
    spring_pos: [f32; 3],
    current_vel: [f32; 3],
    stiff: f32,
    damp: f32,
    gravity: f32,
) -> PyResult<([f32; 3], [f32; 3])> {

    let force_x = rest_pos[0] - spring_pos[0];
    let force_y = rest_pos[1] - spring_pos[1];
    let force_z = rest_pos[2] - spring_pos[2] - gravity;

    let mut new_vel_x = current_vel[0] + (force_x * stiff);
    let mut new_vel_y = current_vel[1] + (force_y * stiff);
    let mut new_vel_z = current_vel[2] + (force_z * stiff);

    new_vel_x *= damp;
    new_vel_y *= damp;
    new_vel_z *= damp;

    let length_squared = (new_vel_x * new_vel_x) + (new_vel_y * new_vel_y) + (new_vel_z * new_vel_z);
    if length_squared > 4.0 {
        let length = length_squared.sqrt();
        if length > 0.0001 {
            let scale = 2.0 / length;
            new_vel_x *= scale;
            new_vel_y *= scale;
            new_vel_z *= scale;
        }
    }

    let new_pos_x = spring_pos[0] + new_vel_x;
    let new_pos_y = spring_pos[1] + new_vel_y;
    let new_pos_z = spring_pos[2] + new_vel_z;

    Ok(([new_pos_x, new_pos_y, new_pos_z], [new_vel_x, new_vel_y, new_vel_z]))
}

#[pymodule]
fn jiggle_rust_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calcular_fisica_frame, m)?)?;
    Ok(())
}
