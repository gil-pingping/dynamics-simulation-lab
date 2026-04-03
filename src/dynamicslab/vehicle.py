from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import rk4_step


@dataclass(slots=True)
class VehicleParameters:
    mass: float = 1500.0
    inertia_z: float = 2500.0
    front_axle_to_cg: float = 1.2
    rear_axle_to_cg: float = 1.6
    front_cornering_stiffness: float = 80000.0
    rear_cornering_stiffness: float = 90000.0
    drag_coefficient: float = 0.38
    rolling_resistance: float = 0.015
    gravity: float = 9.81


@dataclass(slots=True)
class VehicleSample:
    time: float
    x: float
    y: float
    yaw: float
    vx: float
    vy: float
    yaw_rate: float
    steering: float
    longitudinal_accel_cmd: float


def simulate_vehicle_lane_change(
    *,
    duration: float = 8.0,
    dt: float = 0.02,
    params: VehicleParameters | None = None,
) -> list[VehicleSample]:
    params = params or VehicleParameters()
    state = [0.0, 0.0, 0.0, 12.0, 0.0, 0.0]
    samples: list[VehicleSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        steering = steering_profile(time)
        accel_cmd = longitudinal_acceleration_profile(time)
        samples.append(
            VehicleSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                vx=state[3],
                vy=state[4],
                yaw_rate=state[5],
                steering=steering,
                longitudinal_accel_cmd=accel_cmd,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _vehicle_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def steering_profile(time: float) -> float:
    if 1.0 <= time <= 2.6:
        phase = (time - 1.0) / 1.6
        return math.radians(2.8) * math.sin(math.pi * phase)
    if 3.3 <= time <= 4.5:
        phase = (time - 3.3) / 1.2
        return -math.radians(1.0) * math.sin(math.pi * phase)
    return 0.0


def longitudinal_acceleration_profile(time: float) -> float:
    if time < 2.0:
        return 0.7
    if time < 5.5:
        return 0.2
    return 0.0


def _vehicle_derivative(time: float, state: list[float], params: VehicleParameters) -> list[float]:
    x, y, yaw, vx, vy, yaw_rate = state
    steering = steering_profile(time)
    accel_cmd = longitudinal_acceleration_profile(time)

    effective_vx = max(abs(vx), 0.5)
    alpha_front = math.atan2(vy + params.front_axle_to_cg * yaw_rate, effective_vx) - steering
    alpha_rear = math.atan2(vy - params.rear_axle_to_cg * yaw_rate, effective_vx)

    lateral_force_front = -params.front_cornering_stiffness * alpha_front
    lateral_force_rear = -params.rear_cornering_stiffness * alpha_rear

    drag_force = params.drag_coefficient * vx * abs(vx)
    rolling_force = params.rolling_resistance * params.mass * params.gravity * math.copysign(1.0, vx if vx != 0 else 1.0)
    longitudinal_force = params.mass * accel_cmd - drag_force - rolling_force

    x_dot = vx * math.cos(yaw) - vy * math.sin(yaw)
    y_dot = vx * math.sin(yaw) + vy * math.cos(yaw)
    yaw_dot = yaw_rate
    vx_dot = longitudinal_force / params.mass + yaw_rate * vy
    vy_dot = (lateral_force_front * math.cos(steering) + lateral_force_rear) / params.mass - yaw_rate * vx
    yaw_rate_dot = (
        params.front_axle_to_cg * lateral_force_front * math.cos(steering) - params.rear_axle_to_cg * lateral_force_rear
    ) / params.inertia_z

    return [x_dot, y_dot, yaw_dot, vx_dot, vy_dot, yaw_rate_dot]
