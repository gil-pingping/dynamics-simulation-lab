from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import clamp, rk4_step


@dataclass(slots=True)
class DroneParameters:
    mass: float = 1.6
    pitch_inertia: float = 0.035
    gravity: float = 9.81
    max_thrust: float = 32.0
    max_torque: float = 1.8
    max_tilt: float = math.radians(28.0)
    kp_x: float = 1.0
    kd_x: float = 1.5
    kp_z: float = 4.5
    kd_z: float = 3.2
    kp_theta: float = 12.0
    kd_theta: float = 4.5


@dataclass(slots=True)
class DroneSample:
    time: float
    x: float
    z: float
    vx: float
    vz: float
    theta: float
    omega: float
    ref_x: float
    ref_z: float
    thrust: float
    torque: float


def simulate_drone_mission(
    *,
    duration: float = 12.0,
    dt: float = 0.01,
    params: DroneParameters | None = None,
) -> list[DroneSample]:
    params = params or DroneParameters()
    state = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    samples: list[DroneSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        ref_x, ref_z, _, _ = reference_trajectory(time)
        thrust, torque = control_inputs(time, state, params)
        samples.append(
            DroneSample(
                time=time,
                x=state[0],
                z=state[1],
                vx=state[2],
                vz=state[3],
                theta=state[4],
                omega=state[5],
                ref_x=ref_x,
                ref_z=ref_z,
                thrust=thrust,
                torque=torque,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _drone_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def reference_trajectory(time: float) -> tuple[float, float, float, float]:
    if time < 2.0:
        phase = time / 2.0
        ref_x = 0.0
        ref_z = 0.3 + 1.7 * _smoothstep(phase)
        ref_vx = 0.0
        ref_vz = 1.7 * _smoothstep_derivative(phase) / 2.0
        return ref_x, ref_z, ref_vx, ref_vz

    if time < 8.0:
        phase = (time - 2.0) / 6.0
        ref_x = 6.0 * _smoothstep(phase)
        ref_z = 2.0
        ref_vx = 6.0 * _smoothstep_derivative(phase) / 6.0
        ref_vz = 0.0
        return ref_x, ref_z, ref_vx, ref_vz

    if time < 10.0:
        phase = (time - 8.0) / 2.0
        ref_x = 6.0
        ref_z = 2.0 - 0.8 * _smoothstep(phase)
        ref_vx = 0.0
        ref_vz = -0.8 * _smoothstep_derivative(phase) / 2.0
        return ref_x, ref_z, ref_vx, ref_vz

    return 6.0, 1.2, 0.0, 0.0


def control_inputs(time: float, state: list[float], params: DroneParameters) -> tuple[float, float]:
    x, z, vx, vz, theta, omega = state
    ref_x, ref_z, ref_vx, ref_vz = reference_trajectory(time)

    desired_ax = clamp(params.kp_x * (ref_x - x) + params.kd_x * (ref_vx - vx), -3.0, 3.0)
    desired_az = clamp(params.kp_z * (ref_z - z) + params.kd_z * (ref_vz - vz), -4.0, 4.0)

    theta_ref = clamp(-desired_ax / params.gravity, -params.max_tilt, params.max_tilt)
    torque = clamp(
        params.kp_theta * (theta_ref - theta) + params.kd_theta * (0.0 - omega),
        -params.max_torque,
        params.max_torque,
    )
    thrust = clamp(
        params.mass * (params.gravity + desired_az) / max(math.cos(theta), 0.35),
        0.0,
        params.max_thrust,
    )
    return thrust, torque


def _drone_derivative(time: float, state: list[float], params: DroneParameters) -> list[float]:
    thrust, torque = control_inputs(time, state, params)
    _, _, vx, vz, theta, omega = state
    ax = -(thrust / params.mass) * math.sin(theta)
    az = (thrust / params.mass) * math.cos(theta) - params.gravity
    alpha = torque / params.pitch_inertia
    return [vx, vz, ax, az, omega, alpha]


def _smoothstep(phase: float) -> float:
    phase = clamp(phase, 0.0, 1.0)
    return phase * phase * (3.0 - 2.0 * phase)


def _smoothstep_derivative(phase: float) -> float:
    phase = clamp(phase, 0.0, 1.0)
    return 6.0 * phase * (1.0 - phase)
