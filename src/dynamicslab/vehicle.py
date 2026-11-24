from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import clamp, rk4_step


@dataclass(slots=True)
class VehicleParameters:
    mass: float = 1_500.0
    inertia_z: float = 2_500.0
    front_axle_to_cg: float = 1.2
    rear_axle_to_cg: float = 1.6
    cg_height: float = 0.55
    front_cornering_stiffness: float = 85_000.0
    rear_cornering_stiffness: float = 95_000.0
    friction_coefficient: float = 0.95
    drag_coefficient: float = 0.38
    rolling_resistance: float = 0.015
    gravity: float = 9.81
    steering_time_constant: float = 0.18
    max_steering_angle: float = math.radians(8.0)
    max_steering_rate: float = math.radians(140.0)
    preview_time: float = 0.45
    min_preview_distance: float = 6.0
    max_preview_distance: float = 22.0
    cross_track_gain: float = 1.6
    heading_gain: float = 1.9
    yaw_rate_gain: float = 0.2
    speed_kp: float = 0.85
    max_drive_accel: float = 2.2
    max_brake_accel: float = -3.5
    front_drive_bias: float = 0.35
    front_brake_bias: float = 0.62
    lane_width: float = 3.6


@dataclass(slots=True)
class VehicleSample:
    time: float
    x: float
    y: float
    yaw: float
    vx: float
    vy: float
    yaw_rate: float
    speed: float
    steering: float
    steering_cmd: float
    longitudinal_accel_cmd: float
    speed_ref: float
    road_y: float
    road_heading: float
    lateral_error: float
    lateral_accel: float
    front_slip: float
    rear_slip: float
    front_lateral_force: float
    rear_lateral_force: float


@dataclass(slots=True)
class _VehicleResponse:
    steering_cmd: float
    steering_rate: float
    accel_cmd: float
    speed_ref: float
    road_y: float
    road_heading: float
    road_curvature: float
    lateral_error: float
    speed: float
    alpha_front: float
    alpha_rear: float
    lateral_force_front: float
    lateral_force_rear: float
    longitudinal_force_front: float
    longitudinal_force_rear: float
    lateral_accel: float


def simulate_vehicle_lane_change(
    *,
    duration: float = 10.0,
    dt: float = 0.02,
    params: VehicleParameters | None = None,
) -> list[VehicleSample]:
    params = params or VehicleParameters()
    state = [0.0, 0.0, 0.0, 14.0, 0.0, 0.0, 0.0]
    samples: list[VehicleSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        response = _vehicle_response(time, state, params)
        samples.append(
            VehicleSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                vx=state[3],
                vy=state[4],
                yaw_rate=state[5],
                speed=response.speed,
                steering=state[6],
                steering_cmd=response.steering_cmd,
                longitudinal_accel_cmd=response.accel_cmd,
                speed_ref=response.speed_ref,
                road_y=response.road_y,
                road_heading=response.road_heading,
                lateral_error=response.lateral_error,
                lateral_accel=response.lateral_accel,
                front_slip=response.alpha_front,
                rear_slip=response.alpha_rear,
                front_lateral_force=response.lateral_force_front,
                rear_lateral_force=response.lateral_force_rear,
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


def speed_profile(time: float) -> float:
    if time < 1.5:
        return 14.0 + 4.0 * _smoothstep(time / 1.5)
    if time < 4.5:
        return 18.0
    if time < 7.0:
        phase = (time - 4.5) / 2.5
        return 18.0 - 2.5 * _smoothstep(phase)
    if time < 8.8:
        phase = (time - 7.0) / 1.8
        return 15.5 + 2.0 * _smoothstep(phase)
    return 17.5


def road_reference(x: float, params: VehicleParameters) -> tuple[float, float, float]:
    step = 0.5
    y_center = _road_centerline_y(x, params)
    y_forward = _road_centerline_y(x + step, params)
    y_backward = _road_centerline_y(x - step, params)

    dy_dx = (y_forward - y_backward) / (2.0 * step)
    d2y_dx2 = (y_forward - 2.0 * y_center + y_backward) / (step * step)
    heading = math.atan(dy_dx)
    curvature = d2y_dx2 / max((1.0 + dy_dx * dy_dx) ** 1.5, 1e-6)
    return y_center, heading, curvature


def _vehicle_derivative(time: float, state: list[float], params: VehicleParameters) -> list[float]:
    x, y, yaw, vx, vy, yaw_rate, steering = state
    response = _vehicle_response(time, state, params)

    x_dot = vx * math.cos(yaw) - vy * math.sin(yaw)
    y_dot = vx * math.sin(yaw) + vy * math.cos(yaw)
    yaw_dot = yaw_rate
    vx_dot = (
        response.longitudinal_force_rear
        + response.longitudinal_force_front * math.cos(steering)
        - response.lateral_force_front * math.sin(steering)
    ) / params.mass + yaw_rate * vy
    vy_dot = (
        response.lateral_force_front * math.cos(steering)
        + response.lateral_force_rear
        + response.longitudinal_force_front * math.sin(steering)
    ) / params.mass - yaw_rate * vx
    yaw_rate_dot = (
        params.front_axle_to_cg
        * (
            response.lateral_force_front * math.cos(steering)
            + response.longitudinal_force_front * math.sin(steering)
        )
        - params.rear_axle_to_cg * response.lateral_force_rear
    ) / params.inertia_z

    return [x_dot, y_dot, yaw_dot, vx_dot, vy_dot, yaw_rate_dot, response.steering_rate]


def _vehicle_response(time: float, state: list[float], params: VehicleParameters) -> _VehicleResponse:
    x, y, yaw, vx, vy, yaw_rate, steering = state
    speed = math.hypot(vx, vy)
    preview_distance = clamp(
        params.preview_time * max(speed, 3.0),
        params.min_preview_distance,
        params.max_preview_distance,
    )
    road_y, road_heading, road_curvature = road_reference(x + preview_distance, params)
    lateral_error = road_y - y
    heading_error = _wrap_angle(road_heading - yaw)
    speed_ref = speed_profile(time)

    steering_feedback = (
        params.heading_gain * heading_error
        + math.atan2(params.cross_track_gain * lateral_error, max(speed, 4.0))
        - params.yaw_rate_gain * yaw_rate
    )
    wheelbase = params.front_axle_to_cg + params.rear_axle_to_cg
    steering_feedforward = wheelbase * road_curvature
    steering_cmd = clamp(
        steering_feedforward + steering_feedback,
        -params.max_steering_angle,
        params.max_steering_angle,
    )
    steering_rate = clamp(
        (steering_cmd - steering) / params.steering_time_constant,
        -params.max_steering_rate,
        params.max_steering_rate,
    )

    accel_cmd = clamp(
        params.speed_kp * (speed_ref - speed),
        params.max_brake_accel,
        params.max_drive_accel,
    )
    traction_force = params.mass * accel_cmd
    drag_force = params.drag_coefficient * vx * abs(vx)
    rolling_direction = math.copysign(1.0, vx if abs(vx) > 1e-3 else speed_ref)
    rolling_force = params.rolling_resistance * params.mass * params.gravity * rolling_direction
    total_longitudinal_force = traction_force - drag_force - rolling_force

    front_longitudinal_bias = params.front_drive_bias if total_longitudinal_force >= 0.0 else params.front_brake_bias
    longitudinal_force_front = front_longitudinal_bias * total_longitudinal_force
    longitudinal_force_rear = total_longitudinal_force - longitudinal_force_front

    static_front_load = params.mass * params.gravity * params.rear_axle_to_cg / wheelbase
    static_rear_load = params.mass * params.gravity * params.front_axle_to_cg / wheelbase
    load_transfer = params.mass * accel_cmd * params.cg_height / wheelbase
    front_normal_load = max(0.2 * static_front_load, static_front_load - load_transfer)
    rear_normal_load = max(0.2 * static_rear_load, static_rear_load + load_transfer)

    front_lateral_capacity = _combined_slip_capacity(
        params.friction_coefficient,
        front_normal_load,
        longitudinal_force_front,
    )
    rear_lateral_capacity = _combined_slip_capacity(
        params.friction_coefficient,
        rear_normal_load,
        longitudinal_force_rear,
    )

    effective_vx = max(abs(vx), 0.8)
    alpha_front = math.atan2(vy + params.front_axle_to_cg * yaw_rate, effective_vx) - steering
    alpha_rear = math.atan2(vy - params.rear_axle_to_cg * yaw_rate, effective_vx)
    lateral_force_front = _saturated_lateral_force(
        alpha_front,
        params.front_cornering_stiffness,
        front_lateral_capacity,
    )
    lateral_force_rear = _saturated_lateral_force(
        alpha_rear,
        params.rear_cornering_stiffness,
        rear_lateral_capacity,
    )
    lateral_accel = (
        lateral_force_front * math.cos(steering)
        + lateral_force_rear
        + longitudinal_force_front * math.sin(steering)
    ) / params.mass

    return _VehicleResponse(
        steering_cmd=steering_cmd,
        steering_rate=steering_rate,
        accel_cmd=accel_cmd,
        speed_ref=speed_ref,
        road_y=road_y,
        road_heading=road_heading,
        road_curvature=road_curvature,
        lateral_error=lateral_error,
        speed=speed,
        alpha_front=alpha_front,
        alpha_rear=alpha_rear,
        lateral_force_front=lateral_force_front,
        lateral_force_rear=lateral_force_rear,
        longitudinal_force_front=longitudinal_force_front,
        longitudinal_force_rear=longitudinal_force_rear,
        lateral_accel=lateral_accel,
    )


def _road_centerline_y(x: float, params: VehicleParameters) -> float:
    lane_offset = params.lane_width * (
        _smoothstep((x - 24.0) / 16.0) - _smoothstep((x - 62.0) / 18.0)
    )
    recovery_offset = -0.8 * params.lane_width * (
        _smoothstep((x - 96.0) / 16.0) - _smoothstep((x - 126.0) / 18.0)
    )
    return lane_offset + recovery_offset


def _combined_slip_capacity(friction_coefficient: float, normal_load: float, longitudinal_force: float) -> float:
    total_capacity = friction_coefficient * normal_load
    if abs(longitudinal_force) >= total_capacity:
        return 0.0
    return math.sqrt(total_capacity * total_capacity - longitudinal_force * longitudinal_force)


def _saturated_lateral_force(slip_angle: float, cornering_stiffness: float, lateral_capacity: float) -> float:
    if lateral_capacity <= 1e-6:
        return 0.0
    return -lateral_capacity * math.tanh(cornering_stiffness * slip_angle / lateral_capacity)


def _smoothstep(phase: float) -> float:
    phase = clamp(phase, 0.0, 1.0)
    return phase * phase * (3.0 - 2.0 * phase)


def _wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))
