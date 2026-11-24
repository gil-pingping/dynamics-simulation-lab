from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import clamp, rk4_step


@dataclass(slots=True)
class KinematicBicycleParameters:
    wheelbase: float = 2.8
    steering_time_constant: float = 0.22
    max_steering_angle: float = math.radians(34.0)
    max_steering_rate: float = math.radians(110.0)
    speed_kp: float = 1.8
    max_accel: float = 1.6
    max_brake: float = -2.2
    lateral_gain: float = 0.35
    heading_gain: float = 1.8


@dataclass(slots=True)
class KinematicBicycleSample:
    time: float
    x: float
    y: float
    yaw: float
    speed: float
    steering: float
    steering_cmd: float
    speed_ref: float
    ref_x: float
    ref_y: float
    ref_yaw: float
    position_error: float


@dataclass(slots=True)
class AckermannSteeringParameters:
    wheelbase: float = 2.9
    track_width: float = 1.62
    steering_time_constant: float = 0.18
    max_steering_angle: float = math.radians(30.0)
    max_steering_rate: float = math.radians(120.0)
    speed_kp: float = 1.4
    max_accel: float = 1.6
    max_brake: float = -2.0
    lateral_gain: float = 0.28
    heading_gain: float = 1.7


@dataclass(slots=True)
class AckermannSteeringSample:
    time: float
    x: float
    y: float
    yaw: float
    speed: float
    steering: float
    steering_left: float
    steering_right: float
    speed_ref: float
    ref_x: float
    ref_y: float
    position_error: float


@dataclass(slots=True)
class DoubleTrackParameters:
    mass: float = 1_620.0
    inertia_z: float = 2_950.0
    front_axle_to_cg: float = 1.26
    rear_axle_to_cg: float = 1.54
    front_track_width: float = 1.60
    rear_track_width: float = 1.58
    cg_height: float = 0.56
    front_cornering_stiffness: float = 55_000.0
    rear_cornering_stiffness: float = 60_000.0
    friction_coefficient: float = 0.98
    drag_coefficient: float = 0.40
    rolling_resistance: float = 0.016
    gravity: float = 9.81
    steering_time_constant: float = 0.14
    max_steering_angle: float = math.radians(9.0)
    max_steering_rate: float = math.radians(150.0)
    preview_time: float = 0.42
    min_preview_distance: float = 7.0
    max_preview_distance: float = 26.0
    cross_track_gain: float = 1.9
    heading_gain: float = 2.2
    yaw_rate_gain: float = 0.18
    speed_kp: float = 0.75
    max_drive_accel: float = 2.1
    max_brake_accel: float = -3.6
    front_drive_bias: float = 0.25
    front_brake_bias: float = 0.58


@dataclass(slots=True)
class DoubleTrackSample:
    time: float
    x: float
    y: float
    yaw: float
    speed: float
    steering: float
    steering_left: float
    steering_right: float
    speed_ref: float
    road_y: float
    lateral_error: float
    front_left_normal_load: float
    front_right_normal_load: float
    rear_left_normal_load: float
    rear_right_normal_load: float
    front_left_lateral_force: float
    front_right_lateral_force: float
    rear_left_lateral_force: float
    rear_right_lateral_force: float


@dataclass(slots=True)
class SkidSteerParameters:
    mass: float = 820.0
    inertia_z: float = 610.0
    track_width: float = 1.28
    drag_coefficient: float = 0.20
    rolling_resistance: float = 0.025
    gravity: float = 9.81
    yaw_damping: float = 320.0


@dataclass(slots=True)
class SkidSteerSample:
    time: float
    x: float
    y: float
    yaw: float
    speed: float
    yaw_rate: float
    left_force: float
    right_force: float
    turn_radius: float


@dataclass(slots=True)
class ArticulatedVehicleParameters:
    tractor_wheelbase: float = 3.4
    trailer_length: float = 6.2
    steering_time_constant: float = 0.24
    max_steering_angle: float = math.radians(28.0)
    max_steering_rate: float = math.radians(95.0)
    speed_kp: float = 1.2
    max_accel: float = 1.2
    max_brake: float = -2.0
    lateral_gain: float = 0.22
    heading_gain: float = 1.6
    articulation_gain: float = 0.8


@dataclass(slots=True)
class ArticulatedVehicleSample:
    time: float
    x: float
    y: float
    tractor_yaw: float
    trailer_yaw: float
    articulation_angle: float
    speed: float
    steering: float
    steering_cmd: float
    speed_ref: float
    ref_y: float
    lateral_error: float


@dataclass(slots=True)
class DriftVehicleParameters:
    mass: float = 1_450.0
    inertia_z: float = 2_550.0
    front_axle_to_cg: float = 1.20
    rear_axle_to_cg: float = 1.35
    cg_height: float = 0.52
    front_cornering_stiffness: float = 75_000.0
    rear_cornering_stiffness: float = 52_000.0
    mu_front: float = 0.96
    mu_rear: float = 0.76
    drag_coefficient: float = 0.38
    rolling_resistance: float = 0.015
    gravity: float = 9.81
    steering_time_constant: float = 0.10
    max_steering_angle: float = math.radians(24.0)
    max_steering_rate: float = math.radians(220.0)


@dataclass(slots=True)
class DriftVehicleSample:
    time: float
    x: float
    y: float
    yaw: float
    speed: float
    sideslip_deg: float
    yaw_rate: float
    steering: float
    steering_cmd: float
    rear_drive_force: float
    front_slip_deg: float
    rear_slip_deg: float


@dataclass(slots=True)
class OffRoadVehicleParameters:
    wheelbase: float = 2.85
    steering_time_constant: float = 0.20
    max_steering_angle: float = math.radians(30.0)
    max_steering_rate: float = math.radians(120.0)
    speed_kp: float = 0.9
    lateral_gain: float = 0.25
    heading_gain: float = 1.5
    preview_time: float = 0.52
    min_preview_distance: float = 4.0
    max_preview_distance: float = 18.0
    gravity: float = 9.81


@dataclass(slots=True)
class OffRoadVehicleSample:
    time: float
    x: float
    y: float
    yaw: float
    speed: float
    steering: float
    steering_cmd: float
    speed_ref: float
    terrain_height: float
    terrain_pitch_deg: float
    local_friction: float
    lateral_error: float


@dataclass(slots=True)
class FullVehicleParameters:
    mass: float = 1_720.0
    inertia_z: float = 3_150.0
    inertia_roll: float = 720.0
    inertia_pitch: float = 1_520.0
    front_axle_to_cg: float = 1.34
    rear_axle_to_cg: float = 1.56
    front_track_width: float = 1.62
    rear_track_width: float = 1.60
    cg_height: float = 0.58
    wheel_radius: float = 0.34
    wheel_inertia: float = 1.8
    front_cornering_stiffness: float = 48_000.0
    rear_cornering_stiffness: float = 50_000.0
    longitudinal_stiffness: float = 14_000.0
    friction_coefficient: float = 0.97
    gravity: float = 9.81
    steering_time_constant: float = 0.12
    max_steering_angle: float = math.radians(9.0)
    max_steering_rate: float = math.radians(160.0)
    roll_stiffness: float = 45_000.0
    roll_damping: float = 6_500.0
    pitch_stiffness: float = 42_000.0
    pitch_damping: float = 6_000.0
    drag_coefficient: float = 0.42
    rolling_resistance: float = 0.015


@dataclass(slots=True)
class FullVehicleSample:
    time: float
    x: float
    y: float
    yaw: float
    speed: float
    yaw_rate: float
    roll_deg: float
    pitch_deg: float
    steering: float
    wheel_speed_fl: float
    wheel_speed_fr: float
    wheel_speed_rl: float
    wheel_speed_rr: float
    lateral_accel: float
    longitudinal_accel: float


def simulate_kinematic_bicycle_parking(
    *,
    duration: float = 16.0,
    dt: float = 0.05,
    params: KinematicBicycleParameters | None = None,
) -> list[KinematicBicycleSample]:
    params = params or KinematicBicycleParameters()
    state = [0.0, 0.0, 0.0, 0.0, 0.0]
    samples: list[KinematicBicycleSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        ref_x, ref_y, ref_yaw, speed_ref = _parking_reference(time)
        steering_cmd, accel_cmd = _parking_command_profile(time, state[3], params)
        position_error = math.hypot(ref_x - state[0], ref_y - state[1])
        samples.append(
            KinematicBicycleSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                speed=state[3],
                steering=state[4],
                steering_cmd=steering_cmd,
                speed_ref=speed_ref,
                ref_x=ref_x,
                ref_y=ref_y,
                ref_yaw=ref_yaw,
                position_error=position_error,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _kinematic_bicycle_derivative(
                current_time,
                current_state,
                params.wheelbase,
                params.steering_time_constant,
                params.max_steering_rate,
                lambda _, s: _parking_command_profile(current_time, s[3], params),
            ),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def simulate_ackermann_steering_course(
    *,
    duration: float = 18.0,
    dt: float = 0.04,
    params: AckermannSteeringParameters | None = None,
) -> list[AckermannSteeringSample]:
    params = params or AckermannSteeringParameters()
    ref_x, ref_y, ref_yaw, speed_ref = _figure_eight_reference(0.0)
    state = [ref_x, ref_y, ref_yaw, speed_ref, 0.0]
    samples: list[AckermannSteeringSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        ref_x, ref_y, ref_yaw, speed_ref = _figure_eight_reference(time)
        steering_cmd, accel_cmd, position_error = _kinematic_pose_controller(
            state,
            ref_x,
            ref_y,
            ref_yaw,
            speed_ref,
            params.wheelbase,
            params.max_steering_angle,
            params.lateral_gain,
            params.heading_gain,
            params.speed_kp,
            params.max_accel,
            params.max_brake,
        )
        steering_left, steering_right = _ackermann_steering_angles(
            state[4],
            params.wheelbase,
            params.track_width,
        )
        samples.append(
            AckermannSteeringSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                speed=state[3],
                steering=state[4],
                steering_left=steering_left,
                steering_right=steering_right,
                speed_ref=speed_ref,
                ref_x=ref_x,
                ref_y=ref_y,
                position_error=position_error,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _kinematic_bicycle_derivative(
                current_time,
                current_state,
                params.wheelbase,
                params.steering_time_constant,
                params.max_steering_rate,
                lambda _, s: _kinematic_pose_controller(
                    s,
                    *_figure_eight_reference(current_time),
                    params.wheelbase,
                    params.max_steering_angle,
                    params.lateral_gain,
                    params.heading_gain,
                    params.speed_kp,
                    params.max_accel,
                    params.max_brake,
                )[:2],
            ),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def simulate_double_track_obstacle_avoidance(
    *,
    duration: float = 9.0,
    dt: float = 0.02,
    params: DoubleTrackParameters | None = None,
) -> list[DoubleTrackSample]:
    params = params or DoubleTrackParameters()
    state = [0.0, 0.0, 0.0, 16.0, 0.0, 0.0, 0.0]
    samples: list[DoubleTrackSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        response = _double_track_response(time, state, params)
        samples.append(
            DoubleTrackSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                speed=response["speed"],
                steering=state[6],
                steering_left=response["steering_left"],
                steering_right=response["steering_right"],
                speed_ref=response["speed_ref"],
                road_y=response["road_y"],
                lateral_error=response["lateral_error"],
                front_left_normal_load=response["normal_loads"][0],
                front_right_normal_load=response["normal_loads"][1],
                rear_left_normal_load=response["normal_loads"][2],
                rear_right_normal_load=response["normal_loads"][3],
                front_left_lateral_force=response["lateral_forces"][0],
                front_right_lateral_force=response["lateral_forces"][1],
                rear_left_lateral_force=response["lateral_forces"][2],
                rear_right_lateral_force=response["lateral_forces"][3],
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _double_track_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def simulate_skid_steer_maneuver(
    *,
    duration: float = 9.0,
    dt: float = 0.02,
    params: SkidSteerParameters | None = None,
) -> list[SkidSteerSample]:
    params = params or SkidSteerParameters()
    state = [0.0, 0.0, 0.0, 0.0, 0.0]
    samples: list[SkidSteerSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        left_force, right_force = _skid_steer_force_profile(time)
        turn_radius = state[3] / state[4] if abs(state[4]) > 1e-6 else math.inf
        samples.append(
            SkidSteerSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                speed=state[3],
                yaw_rate=state[4],
                left_force=left_force,
                right_force=right_force,
                turn_radius=turn_radius,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _skid_steer_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def simulate_articulated_vehicle_s_curve(
    *,
    duration: float = 12.0,
    dt: float = 0.04,
    params: ArticulatedVehicleParameters | None = None,
) -> list[ArticulatedVehicleSample]:
    params = params or ArticulatedVehicleParameters()
    state = [0.0, 0.0, 0.0, 0.0, 4.0, 0.0]
    samples: list[ArticulatedVehicleSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        ref_y, ref_heading, speed_ref = _articulated_reference(time)
        steering_cmd, accel_cmd, lateral_error = _articulated_controller(state, ref_y, ref_heading, speed_ref, params)
        articulation = _wrap_angle(state[3] - state[2])
        samples.append(
            ArticulatedVehicleSample(
                time=time,
                x=state[0],
                y=state[1],
                tractor_yaw=state[2],
                trailer_yaw=state[3],
                articulation_angle=articulation,
                speed=state[4],
                steering=state[5],
                steering_cmd=steering_cmd,
                speed_ref=speed_ref,
                ref_y=ref_y,
                lateral_error=lateral_error,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _articulated_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def simulate_drift_transition(
    *,
    duration: float = 3.5,
    dt: float = 0.01,
    params: DriftVehicleParameters | None = None,
) -> list[DriftVehicleSample]:
    params = params or DriftVehicleParameters()
    state = [0.0, 0.0, 0.0, 15.5, 0.0, 0.0, 0.0]
    samples: list[DriftVehicleSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        response = _drift_response(time, state, params)
        samples.append(
            DriftVehicleSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                speed=response["speed"],
                sideslip_deg=math.degrees(math.atan2(state[4], max(state[3], 0.1))),
                yaw_rate=state[5],
                steering=state[6],
                steering_cmd=response["steering_cmd"],
                rear_drive_force=response["rear_drive_force"],
                front_slip_deg=math.degrees(response["alpha_front"]),
                rear_slip_deg=math.degrees(response["alpha_rear"]),
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _drift_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def simulate_offroad_traverse(
    *,
    duration: float = 14.0,
    dt: float = 0.04,
    params: OffRoadVehicleParameters | None = None,
) -> list[OffRoadVehicleSample]:
    params = params or OffRoadVehicleParameters()
    state = [0.0, 0.0, 0.0, 4.5, 0.0]
    samples: list[OffRoadVehicleSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        response = _offroad_response(time, state, params)
        samples.append(
            OffRoadVehicleSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                speed=state[3],
                steering=state[4],
                steering_cmd=response["steering_cmd"],
                speed_ref=response["speed_ref"],
                terrain_height=response["terrain_height"],
                terrain_pitch_deg=math.degrees(response["terrain_pitch"]),
                local_friction=response["local_friction"],
                lateral_error=response["lateral_error"],
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _offroad_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def simulate_full_vehicle_ride_and_handling(
    *,
    duration: float = 8.0,
    dt: float = 0.01,
    params: FullVehicleParameters | None = None,
) -> list[FullVehicleSample]:
    params = params or FullVehicleParameters()
    initial_wheel_speed = 16.0 / params.wheel_radius
    state = [
        0.0,
        0.0,
        0.0,
        16.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        initial_wheel_speed,
        initial_wheel_speed,
        initial_wheel_speed,
        initial_wheel_speed,
    ]
    samples: list[FullVehicleSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        response = _full_vehicle_response(time, state, params)
        samples.append(
            FullVehicleSample(
                time=time,
                x=state[0],
                y=state[1],
                yaw=state[2],
                speed=response["speed"],
                yaw_rate=state[5],
                roll_deg=math.degrees(state[6]),
                pitch_deg=math.degrees(state[8]),
                steering=state[10],
                wheel_speed_fl=state[11],
                wheel_speed_fr=state[12],
                wheel_speed_rl=state[13],
                wheel_speed_rr=state[14],
                lateral_accel=response["ay_body"],
                longitudinal_accel=response["ax_body"],
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _full_vehicle_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def _kinematic_bicycle_derivative(
    time: float,
    state: list[float],
    wheelbase: float,
    steering_time_constant: float,
    max_steering_rate: float,
    controller,
) -> list[float]:
    x, y, yaw, speed, steering = state
    steering_cmd, accel_cmd = controller(time, state)
    steering_rate = clamp(
        (steering_cmd - steering) / steering_time_constant,
        -max_steering_rate,
        max_steering_rate,
    )
    x_dot = speed * math.cos(yaw)
    y_dot = speed * math.sin(yaw)
    yaw_dot = speed * math.tan(steering) / wheelbase
    return [x_dot, y_dot, yaw_dot, accel_cmd, steering_rate]


def _kinematic_pose_controller(
    state: list[float],
    ref_x: float,
    ref_y: float,
    ref_yaw: float,
    speed_ref: float,
    wheelbase: float,
    max_steering_angle: float,
    lateral_gain: float,
    heading_gain: float,
    speed_kp: float,
    max_accel: float,
    max_brake: float,
) -> tuple[float, float, float]:
    del wheelbase
    x, y, yaw, speed, _ = state
    dx = ref_x - x
    dy = ref_y - y
    position_error = math.hypot(dx, dy)
    error_x_body = math.cos(yaw) * dx + math.sin(yaw) * dy
    error_y_body = -math.sin(yaw) * dx + math.cos(yaw) * dy
    travel_direction = 1.0 if speed_ref >= 0.0 else -1.0
    heading_error = _wrap_angle(ref_yaw - yaw)
    steering_cmd = clamp(
        travel_direction * lateral_gain * error_y_body + heading_gain * heading_error,
        -max_steering_angle,
        max_steering_angle,
    )
    accel_cmd = clamp(speed_kp * (speed_ref - speed), max_brake, max_accel)
    if abs(error_x_body) < 0.2 and position_error < 0.3 and abs(speed_ref) < 0.15:
        accel_cmd = clamp(-2.0 * speed, max_brake, max_accel)
    return steering_cmd, accel_cmd, position_error


def _parking_reference(time: float) -> tuple[float, float, float, float]:
    if time < 5.0:
        phase = time / 5.0
        return 6.5 * phase, 0.0, 0.0, 2.0
    if time < 9.0:
        phase = (time - 5.0) / 4.0
        return 6.5 - 1.7 * phase, -1.0 * _smoothstep(phase), -math.radians(16.0) * _smoothstep(phase), -1.1
    if time < 13.0:
        phase = (time - 9.0) / 4.0
        return 4.8 - 1.2 * phase, -1.0 - 0.8 * _smoothstep(phase), -math.radians(16.0) + math.radians(7.0) * _smoothstep(phase), -1.0
    if time < 15.0:
        phase = (time - 13.0) / 2.0
        return 3.6 - 0.3 * phase, -1.8 + 0.05 * _smoothstep(phase), -math.radians(9.0) * (1.0 - _smoothstep(phase)), 0.5
    return 3.3, -1.75, -math.radians(9.0), 0.0


def _parking_command_profile(
    time: float,
    speed: float,
    params: KinematicBicycleParameters,
) -> tuple[float, float]:
    if time < 5.0:
        steering_cmd = 0.0
        speed_ref = 2.0
    elif time < 9.0:
        steering_cmd = math.radians(-34.0)
        speed_ref = -1.1
    elif time < 13.0:
        steering_cmd = math.radians(30.0)
        speed_ref = -1.0
    elif time < 15.0:
        steering_cmd = 0.0
        speed_ref = 0.5
    else:
        steering_cmd = 0.0
        speed_ref = 0.0
    accel_cmd = clamp(params.speed_kp * (speed_ref - speed), params.max_brake, params.max_accel)
    return clamp(steering_cmd, -params.max_steering_angle, params.max_steering_angle), accel_cmd


def _figure_eight_reference(time: float) -> tuple[float, float, float, float]:
    omega = 0.30
    x = 14.0 * math.sin(omega * time)
    y = 6.0 * math.sin(2.0 * omega * time)
    dx_dt = 14.0 * omega * math.cos(omega * time)
    dy_dt = 12.0 * omega * math.cos(2.0 * omega * time)
    yaw = math.atan2(dy_dt, dx_dt)
    speed = math.hypot(dx_dt, dy_dt)
    return x, y, yaw, speed


def _double_track_derivative(time: float, state: list[float], params: DoubleTrackParameters) -> list[float]:
    x, y, yaw, u, v, yaw_rate, steering = state
    response = _double_track_response(time, state, params)
    total_force_x, total_force_y = response["total_force"]
    yaw_moment = response["yaw_moment"]
    x_dot = u * math.cos(yaw) - v * math.sin(yaw)
    y_dot = u * math.sin(yaw) + v * math.cos(yaw)
    yaw_dot = yaw_rate
    u_dot = total_force_x / params.mass + yaw_rate * v
    v_dot = total_force_y / params.mass - yaw_rate * u
    yaw_rate_dot = yaw_moment / params.inertia_z
    steering_rate = clamp(
        (response["steering_cmd"] - steering) / params.steering_time_constant,
        -params.max_steering_rate,
        params.max_steering_rate,
    )
    return [x_dot, y_dot, yaw_dot, u_dot, v_dot, yaw_rate_dot, steering_rate]


def _double_track_response(time: float, state: list[float], params: DoubleTrackParameters) -> dict[str, object]:
    x, y, yaw, u, v, yaw_rate, steering = state
    speed = math.hypot(u, v)
    preview_distance = clamp(
        params.preview_time * max(speed, 4.0),
        params.min_preview_distance,
        params.max_preview_distance,
    )
    road_y, road_heading, road_curvature = _double_track_road_reference(x + preview_distance)
    lateral_error = road_y - y
    heading_error = _wrap_angle(road_heading - yaw)
    wheelbase = params.front_axle_to_cg + params.rear_axle_to_cg
    steering_feedback = (
        params.heading_gain * heading_error
        + math.atan2(params.cross_track_gain * lateral_error, max(speed, 4.0))
        - params.yaw_rate_gain * yaw_rate
    )
    steering_cmd = clamp(
        wheelbase * road_curvature + steering_feedback,
        -params.max_steering_angle,
        params.max_steering_angle,
    )
    steering_left, steering_right = _ackermann_steering_angles(steering, wheelbase, params.front_track_width)

    speed_ref = _double_track_speed_profile(time)
    accel_cmd = clamp(
        params.speed_kp * (speed_ref - speed),
        params.max_brake_accel,
        params.max_drive_accel,
    )
    total_longitudinal_force = (
        params.mass * accel_cmd
        - params.drag_coefficient * u * abs(u)
        - params.rolling_resistance * params.mass * params.gravity * math.copysign(1.0, u if abs(u) > 1e-3 else 1.0)
    )
    front_bias = params.front_drive_bias if total_longitudinal_force >= 0.0 else params.front_brake_bias
    axle_force_front = front_bias * total_longitudinal_force
    axle_force_rear = total_longitudinal_force - axle_force_front
    longitudinal_forces = [
        0.5 * axle_force_front,
        0.5 * axle_force_front,
        0.5 * axle_force_rear,
        0.5 * axle_force_rear,
    ]

    ay_guess = yaw_rate * max(u, 0.0)
    normal_loads = _four_wheel_normal_loads(
        params.mass,
        params.gravity,
        params.front_axle_to_cg,
        params.rear_axle_to_cg,
        params.front_track_width,
        params.rear_track_width,
        params.cg_height,
        accel_cmd,
        ay_guess,
    )
    wheel_positions = [
        (params.front_axle_to_cg, 0.5 * params.front_track_width),
        (params.front_axle_to_cg, -0.5 * params.front_track_width),
        (-params.rear_axle_to_cg, 0.5 * params.rear_track_width),
        (-params.rear_axle_to_cg, -0.5 * params.rear_track_width),
    ]
    wheel_steering = [steering_left, steering_right, 0.0, 0.0]
    cornering_stiffness = [
        params.front_cornering_stiffness,
        params.front_cornering_stiffness,
        params.rear_cornering_stiffness,
        params.rear_cornering_stiffness,
    ]

    total_force_x = 0.0
    total_force_y = 0.0
    yaw_moment = 0.0
    lateral_forces: list[float] = []

    for (wheel_x, wheel_y), normal_load, wheel_delta, wheel_force_x, wheel_stiffness in zip(
        wheel_positions,
        normal_loads,
        wheel_steering,
        longitudinal_forces,
        cornering_stiffness,
        strict=True,
    ):
        vx_wheel = u - yaw_rate * wheel_y
        vy_wheel = v + yaw_rate * wheel_x
        alpha = math.atan2(vy_wheel, max(abs(vx_wheel), 0.8)) - wheel_delta
        lateral_capacity = _combined_slip_capacity(params.friction_coefficient, normal_load, wheel_force_x)
        wheel_force_y = _saturated_lateral_force(alpha, wheel_stiffness, lateral_capacity)
        lateral_forces.append(wheel_force_y)
        body_force_x = wheel_force_x * math.cos(wheel_delta) - wheel_force_y * math.sin(wheel_delta)
        body_force_y = wheel_force_x * math.sin(wheel_delta) + wheel_force_y * math.cos(wheel_delta)
        total_force_x += body_force_x
        total_force_y += body_force_y
        yaw_moment += wheel_x * body_force_y - wheel_y * body_force_x

    return {
        "speed": speed,
        "speed_ref": speed_ref,
        "road_y": road_y,
        "lateral_error": lateral_error,
        "steering_cmd": steering_cmd,
        "steering_left": steering_left,
        "steering_right": steering_right,
        "normal_loads": normal_loads,
        "lateral_forces": lateral_forces,
        "total_force": (total_force_x, total_force_y),
        "yaw_moment": yaw_moment,
    }


def _double_track_road_reference(x: float) -> tuple[float, float, float]:
    step = 0.5
    y_center = _double_track_centerline_y(x)
    y_forward = _double_track_centerline_y(x + step)
    y_backward = _double_track_centerline_y(x - step)
    dy_dx = (y_forward - y_backward) / (2.0 * step)
    d2y_dx2 = (y_forward - 2.0 * y_center + y_backward) / (step * step)
    heading = math.atan(dy_dx)
    curvature = d2y_dx2 / max((1.0 + dy_dx * dy_dx) ** 1.5, 1e-6)
    return y_center, heading, curvature


def _double_track_centerline_y(x: float) -> float:
    return 3.2 * (_smoothstep((x - 22.0) / 14.0) - _smoothstep((x - 52.0) / 16.0)) - 2.7 * (
        _smoothstep((x - 82.0) / 14.0) - _smoothstep((x - 112.0) / 16.0)
    )


def _double_track_speed_profile(time: float) -> float:
    if time < 2.0:
        return 16.0 + 2.5 * _smoothstep(time / 2.0)
    if time < 5.0:
        return 18.5
    if time < 7.5:
        return 18.5 - 1.5 * _smoothstep((time - 5.0) / 2.5)
    return 17.0


def _four_wheel_normal_loads(
    mass: float,
    gravity: float,
    front_axle_to_cg: float,
    rear_axle_to_cg: float,
    front_track_width: float,
    rear_track_width: float,
    cg_height: float,
    longitudinal_accel: float,
    lateral_accel: float,
) -> list[float]:
    wheelbase = front_axle_to_cg + rear_axle_to_cg
    static_front = mass * gravity * rear_axle_to_cg / wheelbase
    static_rear = mass * gravity * front_axle_to_cg / wheelbase
    transfer_longitudinal = mass * longitudinal_accel * cg_height / wheelbase
    front_total = static_front - transfer_longitudinal
    rear_total = static_rear + transfer_longitudinal
    front_lateral_transfer = 0.55 * mass * lateral_accel * cg_height / front_track_width
    rear_lateral_transfer = 0.45 * mass * lateral_accel * cg_height / rear_track_width
    return [
        max(0.1 * static_front, 0.5 * front_total - 0.5 * front_lateral_transfer),
        max(0.1 * static_front, 0.5 * front_total + 0.5 * front_lateral_transfer),
        max(0.1 * static_rear, 0.5 * rear_total - 0.5 * rear_lateral_transfer),
        max(0.1 * static_rear, 0.5 * rear_total + 0.5 * rear_lateral_transfer),
    ]


def _skid_steer_derivative(time: float, state: list[float], params: SkidSteerParameters) -> list[float]:
    x, y, yaw, speed, yaw_rate = state
    left_force, right_force = _skid_steer_force_profile(time)
    drag_force = params.drag_coefficient * speed * abs(speed)
    rolling_force = params.rolling_resistance * params.mass * params.gravity * math.copysign(1.0, speed if abs(speed) > 1e-3 else 1.0)
    scrub_force = 0.10 * params.mass * abs(yaw_rate) * params.track_width
    total_force = left_force + right_force - drag_force - rolling_force - scrub_force
    speed_dot = total_force / params.mass
    yaw_rate_dot = (
        0.5 * params.track_width * (right_force - left_force) - params.yaw_damping * yaw_rate
    ) / params.inertia_z
    x_dot = speed * math.cos(yaw)
    y_dot = speed * math.sin(yaw)
    return [x_dot, y_dot, yaw_rate, speed_dot, yaw_rate_dot]


def _skid_steer_force_profile(time: float) -> tuple[float, float]:
    if time < 2.0:
        phase = time / 2.0
        force = 1_400.0 + 300.0 * _smoothstep(phase)
        return force, force
    if time < 3.0:
        return 1_350.0, -1_350.0
    if time < 6.2:
        return 1_350.0, 2_050.0
    if time < 7.4:
        return -500.0, -350.0
    return 0.0, 0.0


def _articulated_derivative(
    time: float,
    state: list[float],
    params: ArticulatedVehicleParameters,
) -> list[float]:
    x, y, tractor_yaw, trailer_yaw, speed, steering = state
    steering_cmd, accel_cmd, _ = _articulated_controller(
        state,
        *_articulated_reference(time),
        params,
    )
    steering_rate = clamp(
        (steering_cmd - steering) / params.steering_time_constant,
        -params.max_steering_rate,
        params.max_steering_rate,
    )
    x_dot = speed * math.cos(tractor_yaw)
    y_dot = speed * math.sin(tractor_yaw)
    tractor_yaw_dot = speed * math.tan(steering) / params.tractor_wheelbase
    trailer_yaw_dot = speed * math.sin(tractor_yaw - trailer_yaw) / params.trailer_length
    return [x_dot, y_dot, tractor_yaw_dot, trailer_yaw_dot, accel_cmd, steering_rate]


def _articulated_reference(time: float) -> tuple[float, float, float]:
    if time < 3.0:
        return 0.0, 0.0, 4.2
    if time < 7.0:
        phase = (time - 3.0) / 4.0
        return 2.0 * math.sin(math.pi * phase), math.radians(10.0) * math.sin(math.pi * phase), 4.4
    if time < 10.5:
        phase = (time - 7.0) / 3.5
        return -1.5 * math.sin(math.pi * phase), -math.radians(8.0) * math.sin(math.pi * phase), 4.0
    return 0.0, 0.0, 3.5


def _articulated_controller(
    state: list[float],
    ref_y: float,
    ref_heading: float,
    speed_ref: float,
    params: ArticulatedVehicleParameters,
) -> tuple[float, float, float]:
    _, y, tractor_yaw, trailer_yaw, speed, _ = state
    lateral_error = ref_y - y
    articulation = _wrap_angle(trailer_yaw - tractor_yaw)
    heading_error = _wrap_angle(ref_heading - tractor_yaw)
    steering_cmd = clamp(
        params.lateral_gain * lateral_error
        + params.heading_gain * heading_error
        - params.articulation_gain * articulation,
        -params.max_steering_angle,
        params.max_steering_angle,
    )
    accel_cmd = clamp(params.speed_kp * (speed_ref - speed), params.max_brake, params.max_accel)
    return steering_cmd, accel_cmd, lateral_error


def _drift_derivative(time: float, state: list[float], params: DriftVehicleParameters) -> list[float]:
    x, y, yaw, u, v, yaw_rate, steering = state
    response = _drift_response(time, state, params)
    total_force_x = response["force_x"]
    total_force_y = response["force_y"]
    yaw_moment = response["yaw_moment"]
    x_dot = u * math.cos(yaw) - v * math.sin(yaw)
    y_dot = u * math.sin(yaw) + v * math.cos(yaw)
    yaw_dot = yaw_rate
    u_dot = total_force_x / params.mass + yaw_rate * v
    v_dot = total_force_y / params.mass - yaw_rate * u
    yaw_rate_dot = yaw_moment / params.inertia_z
    steering_rate = clamp(
        (response["steering_cmd"] - steering) / params.steering_time_constant,
        -params.max_steering_rate,
        params.max_steering_rate,
    )
    return [x_dot, y_dot, yaw_dot, u_dot, v_dot, yaw_rate_dot, steering_rate]


def _drift_response(time: float, state: list[float], params: DriftVehicleParameters) -> dict[str, float]:
    _, _, _, u, v, yaw_rate, steering = state
    speed = math.hypot(u, v)
    steering_cmd = _drift_steering_profile(time)
    rear_drive_force = _drift_rear_drive_force_profile(time)
    wheelbase = params.front_axle_to_cg + params.rear_axle_to_cg
    drag_force = params.drag_coefficient * u * abs(u)
    rolling_force = params.rolling_resistance * params.mass * params.gravity * math.copysign(1.0, u if abs(u) > 1e-3 else 1.0)
    axle_force_front = 0.0
    axle_force_rear = rear_drive_force - drag_force - rolling_force
    ax_guess = axle_force_rear / params.mass
    static_front = params.mass * params.gravity * params.rear_axle_to_cg / wheelbase
    static_rear = params.mass * params.gravity * params.front_axle_to_cg / wheelbase
    transfer_longitudinal = params.mass * ax_guess * params.cg_height / wheelbase
    normal_front = max(0.35 * static_front, static_front - transfer_longitudinal)
    normal_rear = max(0.35 * static_rear, static_rear + transfer_longitudinal)

    alpha_front = math.atan2(v + params.front_axle_to_cg * yaw_rate, max(abs(u), 1.0)) - steering
    alpha_rear = math.atan2(v - params.rear_axle_to_cg * yaw_rate, max(abs(u), 1.0))
    lateral_capacity_front = _combined_slip_capacity(params.mu_front, normal_front, axle_force_front)
    lateral_capacity_rear = _combined_slip_capacity(params.mu_rear, normal_rear, axle_force_rear)
    lateral_force_front = _saturated_lateral_force(alpha_front, params.front_cornering_stiffness, lateral_capacity_front)
    lateral_force_rear = _saturated_lateral_force(alpha_rear, params.rear_cornering_stiffness, lateral_capacity_rear)

    total_force_x = axle_force_front * math.cos(steering) - lateral_force_front * math.sin(steering) + axle_force_rear
    total_force_y = axle_force_front * math.sin(steering) + lateral_force_front * math.cos(steering) + lateral_force_rear
    yaw_moment = params.front_axle_to_cg * (
        axle_force_front * math.sin(steering) + lateral_force_front * math.cos(steering)
    ) - params.rear_axle_to_cg * lateral_force_rear

    return {
        "speed": speed,
        "steering_cmd": steering_cmd,
        "rear_drive_force": rear_drive_force,
        "alpha_front": alpha_front,
        "alpha_rear": alpha_rear,
        "force_x": total_force_x,
        "force_y": total_force_y,
        "yaw_moment": yaw_moment,
    }


def _drift_steering_profile(time: float) -> float:
    if time < 1.0:
        return 0.0
    if time < 1.6:
        return math.radians(6.5) * _smoothstep((time - 1.0) / 0.6)
    if time < 2.3:
        phase = (time - 1.6) / 0.7
        return math.radians(6.5) - math.radians(12.5) * _smoothstep(phase)
    if time < 3.5:
        return math.radians(-3.0)
    return 0.0


def _drift_rear_drive_force_profile(time: float) -> float:
    if time < 1.0:
        return 1_400.0
    if time < 2.5:
        return 3_000.0
    if time < 4.0:
        return 1_800.0
    return 800.0


def _offroad_derivative(time: float, state: list[float], params: OffRoadVehicleParameters) -> list[float]:
    x, y, yaw, speed, steering = state
    response = _offroad_response(time, state, params)
    steering_rate = clamp(
        (response["steering_cmd"] - steering) / params.steering_time_constant,
        -params.max_steering_rate,
        params.max_steering_rate,
    )
    x_dot = speed * math.cos(yaw)
    y_dot = speed * math.sin(yaw)
    yaw_dot = speed * math.tan(steering) / params.wheelbase
    return [x_dot, y_dot, yaw_dot, response["accel_cmd"], steering_rate]


def _offroad_response(time: float, state: list[float], params: OffRoadVehicleParameters) -> dict[str, float]:
    x, y, yaw, speed, _ = state
    speed_ref = _offroad_speed_profile(time)
    preview_distance = clamp(
        params.preview_time * max(speed, 2.0),
        params.min_preview_distance,
        params.max_preview_distance,
    )
    ref_y, ref_heading = _offroad_path_reference(x + preview_distance)
    lateral_error = ref_y - y
    heading_error = _wrap_angle(ref_heading - yaw)
    steering_cmd = clamp(
        params.lateral_gain * lateral_error + params.heading_gain * heading_error,
        -params.max_steering_angle,
        params.max_steering_angle,
    )
    terrain_height = _terrain_height(x, y)
    terrain_pitch = _terrain_pitch(x, y)
    local_friction = _terrain_friction(x, y)
    grade_term = params.gravity * math.sin(terrain_pitch)
    accel_limit = local_friction * params.gravity * 0.32
    brake_limit = -local_friction * params.gravity * 0.45
    accel_cmd = clamp(params.speed_kp * (speed_ref - speed) - grade_term, brake_limit, accel_limit)
    return {
        "steering_cmd": steering_cmd,
        "speed_ref": speed_ref,
        "terrain_height": terrain_height,
        "terrain_pitch": terrain_pitch,
        "local_friction": local_friction,
        "lateral_error": lateral_error,
        "accel_cmd": accel_cmd,
    }


def _offroad_speed_profile(time: float) -> float:
    if time < 4.0:
        return 5.5
    if time < 9.0:
        return 6.8
    return 6.0


def _offroad_path_reference(x: float) -> tuple[float, float]:
    step = 0.5
    center = 1.4 * math.sin(0.06 * x) + 0.9 * math.sin(0.13 * x)
    forward = 1.4 * math.sin(0.06 * (x + step)) + 0.9 * math.sin(0.13 * (x + step))
    backward = 1.4 * math.sin(0.06 * (x - step)) + 0.9 * math.sin(0.13 * (x - step))
    heading = math.atan((forward - backward) / (2.0 * step))
    return center, heading


def _terrain_height(x: float, y: float) -> float:
    return 0.50 * math.sin(0.08 * x) + 0.25 * math.cos(0.18 * y) + 0.15 * math.sin(0.05 * (x + y))


def _terrain_pitch(x: float, y: float) -> float:
    del y
    dh_dx = 0.04 * math.cos(0.08 * x) + 0.0075 * math.cos(0.05 * x)
    return math.atan(dh_dx)


def _terrain_friction(x: float, y: float) -> float:
    del y
    friction = 0.88
    friction -= 0.22 * (_smoothstep((x - 25.0) / 10.0) - _smoothstep((x - 55.0) / 10.0))
    friction -= 0.15 * (_smoothstep((x - 75.0) / 12.0) - _smoothstep((x - 95.0) / 12.0))
    return clamp(friction, 0.45, 0.90)


def _full_vehicle_derivative(time: float, state: list[float], params: FullVehicleParameters) -> list[float]:
    x, y, yaw, u, v, yaw_rate, roll, roll_rate, pitch, pitch_rate, steering, omega_fl, omega_fr, omega_rl, omega_rr = state
    response = _full_vehicle_response(time, state, params)
    x_dot = u * math.cos(yaw) - v * math.sin(yaw)
    y_dot = u * math.sin(yaw) + v * math.cos(yaw)
    yaw_dot = yaw_rate
    steering_rate = clamp(
        (response["steering_cmd"] - steering) / params.steering_time_constant,
        -params.max_steering_rate,
        params.max_steering_rate,
    )
    return [
        x_dot,
        y_dot,
        yaw_dot,
        response["ax_body"] + yaw_rate * v,
        response["ay_body"] - yaw_rate * u,
        response["yaw_accel"],
        roll_rate,
        response["roll_accel"],
        pitch_rate,
        response["pitch_accel"],
        steering_rate,
        response["wheel_accels"][0],
        response["wheel_accels"][1],
        response["wheel_accels"][2],
        response["wheel_accels"][3],
    ]


def _full_vehicle_response(time: float, state: list[float], params: FullVehicleParameters) -> dict[str, object]:
    _, _, _, u, v, yaw_rate, roll, roll_rate, pitch, pitch_rate, steering, omega_fl, omega_fr, omega_rl, omega_rr = state
    wheelbase = params.front_axle_to_cg + params.rear_axle_to_cg
    steering_cmd = _full_vehicle_steering_profile(time)
    drive_torque = _full_vehicle_drive_torque_profile(time)
    brake_torque = _full_vehicle_brake_torque_profile(time)
    steering_left, steering_right = _ackermann_steering_angles(steering, wheelbase, params.front_track_width)
    ay_guess = yaw_rate * max(u, 0.0)
    normal_loads = _full_vehicle_normal_loads(roll, roll_rate, pitch, pitch_rate, ay_guess, params)
    wheel_positions = [
        (params.front_axle_to_cg, 0.5 * params.front_track_width),
        (params.front_axle_to_cg, -0.5 * params.front_track_width),
        (-params.rear_axle_to_cg, 0.5 * params.rear_track_width),
        (-params.rear_axle_to_cg, -0.5 * params.rear_track_width),
    ]
    wheel_steering = [steering_left, steering_right, 0.0, 0.0]
    cornering_stiffness = [
        params.front_cornering_stiffness,
        params.front_cornering_stiffness,
        params.rear_cornering_stiffness,
        params.rear_cornering_stiffness,
    ]
    wheel_speeds = [omega_fl, omega_fr, omega_rl, omega_rr]
    drive_torques = [0.0, 0.0, drive_torque, drive_torque]
    brake_torques = [0.7 * brake_torque, 0.7 * brake_torque, 0.3 * brake_torque, 0.3 * brake_torque]

    total_force_x = 0.0
    total_force_y = 0.0
    yaw_moment = 0.0
    wheel_accels: list[float] = []

    for (wheel_x, wheel_y), wheel_delta, normal_load, wheel_speed, wheel_drive, wheel_brake, wheel_stiffness in zip(
        wheel_positions,
        wheel_steering,
        normal_loads,
        wheel_speeds,
        drive_torques,
        brake_torques,
        cornering_stiffness,
        strict=True,
    ):
        vx_body = u - yaw_rate * wheel_y
        vy_body = v + yaw_rate * wheel_x
        vx_wheel = math.cos(wheel_delta) * vx_body + math.sin(wheel_delta) * vy_body
        vy_wheel = -math.sin(wheel_delta) * vx_body + math.cos(wheel_delta) * vy_body
        slip_ratio = (params.wheel_radius * wheel_speed - vx_wheel) / max(abs(vx_wheel), 1.0)
        slip_angle = math.atan2(vy_wheel, max(abs(vx_wheel), 0.8))
        force_x_wheel = params.longitudinal_stiffness * slip_ratio
        force_y_wheel = -wheel_stiffness * slip_angle
        force_x_wheel, force_y_wheel = _saturate_force_pair(force_x_wheel, force_y_wheel, params.friction_coefficient * normal_load)
        body_force_x = force_x_wheel * math.cos(wheel_delta) - force_y_wheel * math.sin(wheel_delta)
        body_force_y = force_x_wheel * math.sin(wheel_delta) + force_y_wheel * math.cos(wheel_delta)
        total_force_x += body_force_x
        total_force_y += body_force_y
        yaw_moment += wheel_x * body_force_y - wheel_y * body_force_x
        brake_sign = math.copysign(1.0, wheel_speed if abs(wheel_speed) > 0.5 else vx_wheel if abs(vx_wheel) > 0.5 else 1.0)
        wheel_accels.append(
            (wheel_drive - wheel_brake * brake_sign - force_x_wheel * params.wheel_radius) / params.wheel_inertia
        )

    drag_force = params.drag_coefficient * u * abs(u)
    rolling_force = params.rolling_resistance * params.mass * params.gravity * math.copysign(1.0, u if abs(u) > 1e-3 else 1.0)
    total_force_x -= drag_force + rolling_force

    ax_body = total_force_x / params.mass
    ay_body = total_force_y / params.mass
    roll_accel = (params.mass * params.cg_height * ay_body - params.roll_stiffness * roll - params.roll_damping * roll_rate) / params.inertia_roll
    pitch_accel = (-params.mass * params.cg_height * ax_body - params.pitch_stiffness * pitch - params.pitch_damping * pitch_rate) / params.inertia_pitch

    return {
        "speed": math.hypot(u, v),
        "steering_cmd": steering_cmd,
        "ax_body": ax_body,
        "ay_body": ay_body,
        "yaw_accel": yaw_moment / params.inertia_z,
        "roll_accel": roll_accel,
        "pitch_accel": pitch_accel,
        "wheel_accels": wheel_accels,
    }


def _full_vehicle_normal_loads(
    roll: float,
    roll_rate: float,
    pitch: float,
    pitch_rate: float,
    lateral_accel: float,
    params: FullVehicleParameters,
) -> list[float]:
    wheelbase = params.front_axle_to_cg + params.rear_axle_to_cg
    static_front = params.mass * params.gravity * params.rear_axle_to_cg / wheelbase
    static_rear = params.mass * params.gravity * params.front_axle_to_cg / wheelbase
    pitch_transfer = (params.pitch_stiffness * pitch + params.pitch_damping * pitch_rate) / wheelbase
    roll_transfer_total = params.roll_stiffness * roll + params.roll_damping * roll_rate + params.mass * params.cg_height * lateral_accel
    front_total = static_front - pitch_transfer
    rear_total = static_rear + pitch_transfer
    front_roll = 0.55 * roll_transfer_total / params.front_track_width
    rear_roll = 0.45 * roll_transfer_total / params.rear_track_width
    return [
        max(0.1 * static_front, 0.5 * front_total + 0.5 * front_roll),
        max(0.1 * static_front, 0.5 * front_total - 0.5 * front_roll),
        max(0.1 * static_rear, 0.5 * rear_total + 0.5 * rear_roll),
        max(0.1 * static_rear, 0.5 * rear_total - 0.5 * rear_roll),
    ]


def _full_vehicle_steering_profile(time: float) -> float:
    if 1.0 <= time <= 2.8:
        return math.radians(5.5) * math.sin(math.pi * (time - 1.0) / 1.8)
    if 3.2 <= time <= 5.0:
        return -math.radians(3.0) * math.sin(math.pi * (time - 3.2) / 1.8)
    return 0.0


def _full_vehicle_drive_torque_profile(time: float) -> float:
    if time < 1.0:
        return 140.0
    if time < 4.5:
        return 260.0
    if time < 6.0:
        return 120.0
    return 0.0


def _full_vehicle_brake_torque_profile(time: float) -> float:
    if 6.0 <= time <= 7.3:
        return 180.0
    return 0.0


def _ackermann_steering_angles(steering: float, wheelbase: float, track_width: float) -> tuple[float, float]:
    if abs(steering) < 1e-6:
        return steering, steering
    turn_radius = wheelbase / max(abs(math.tan(steering)), 1e-6)
    inner_radius = max(turn_radius - 0.5 * track_width, 0.3)
    outer_radius = turn_radius + 0.5 * track_width
    inner_angle = math.atan(wheelbase / inner_radius)
    outer_angle = math.atan(wheelbase / outer_radius)
    if steering > 0.0:
        return inner_angle, outer_angle
    return -outer_angle, -inner_angle


def _combined_slip_capacity(friction_coefficient: float, normal_load: float, longitudinal_force: float) -> float:
    total_capacity = friction_coefficient * max(normal_load, 0.0)
    if abs(longitudinal_force) >= total_capacity:
        return 0.0
    return math.sqrt(max(total_capacity * total_capacity - longitudinal_force * longitudinal_force, 0.0))


def _saturated_lateral_force(slip_angle: float, cornering_stiffness: float, lateral_capacity: float) -> float:
    if lateral_capacity <= 1e-6:
        return 0.0
    return -lateral_capacity * math.tanh(cornering_stiffness * slip_angle / lateral_capacity)


def _saturate_force_pair(force_x: float, force_y: float, capacity: float) -> tuple[float, float]:
    if capacity <= 1e-6:
        return 0.0, 0.0
    usage = math.hypot(force_x, force_y)
    if usage <= capacity:
        return force_x, force_y
    scale = capacity / usage
    return force_x * scale, force_y * scale


def _smoothstep(phase: float) -> float:
    phase = clamp(phase, 0.0, 1.0)
    return phase * phase * (3.0 - 2.0 * phase)


def _wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))
