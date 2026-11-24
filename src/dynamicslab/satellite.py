from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import clamp, rk4_step


@dataclass(slots=True)
class SatelliteParameters:
    earth_gravitational_parameter: float = 3.986004418e14
    earth_radius: float = 6_371_000.0
    initial_altitude: float = 400_000.0
    thrust_acceleration: float = 0.08
    body_inertia_z: float = 85.0
    wheel_inertia: float = 0.12
    max_wheel_torque: float = 0.045
    max_wheel_speed: float = 90.0
    attitude_kp: float = 0.16
    attitude_kd: float = 4.8
    initial_attitude_offset: float = math.radians(18.0)


@dataclass(slots=True)
class SatelliteSample:
    time: float
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    altitude: float
    speed: float
    specific_energy: float
    thrust_accel: float
    theta: float
    theta_ref: float
    omega: float
    wheel_speed: float
    wheel_torque: float
    pointing_error_deg: float


def simulate_satellite_orbit_raise(
    *,
    duration: float = 10_800.0,
    dt: float = 5.0,
    params: SatelliteParameters | None = None,
) -> list[SatelliteSample]:
    params = params or SatelliteParameters()
    initial_radius = params.earth_radius + params.initial_altitude
    circular_speed = math.sqrt(params.earth_gravitational_parameter / initial_radius)
    initial_theta_ref = math.pi / 2.0

    state = [
        initial_radius,
        0.0,
        0.0,
        circular_speed,
        initial_theta_ref + params.initial_attitude_offset,
        0.0,
        0.0,
    ]
    samples: list[SatelliteSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        thrust_accel = thrust_profile(time)
        theta_ref, _ = attitude_reference(state)
        wheel_torque = reaction_wheel_torque(state, params)
        radius = math.hypot(state[0], state[1])
        speed = math.hypot(state[2], state[3])
        pointing_error = _wrap_angle(theta_ref - state[4])
        samples.append(
            SatelliteSample(
                time=time,
                x=state[0],
                y=state[1],
                vx=state[2],
                vy=state[3],
                radius=radius,
                altitude=radius - params.earth_radius,
                speed=speed,
                specific_energy=0.5 * speed * speed - params.earth_gravitational_parameter / radius,
                thrust_accel=thrust_accel,
                theta=state[4],
                theta_ref=theta_ref,
                omega=state[5],
                wheel_speed=state[6] / params.wheel_inertia,
                wheel_torque=wheel_torque,
                pointing_error_deg=math.degrees(pointing_error),
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _satellite_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def thrust_profile(time: float) -> float:
    if 900.0 <= time <= 2_400.0:
        return 0.08
    return 0.0


def attitude_reference(state: list[float]) -> tuple[float, float]:
    x, y, vx, vy, *_ = state
    speed = math.hypot(vx, vy)
    if speed < 1e-9:
        return 0.0, 0.0

    theta_ref = math.atan2(vy, vx)
    radius_squared = max(x * x + y * y, 1.0)
    orbital_rate = (x * vy - y * vx) / radius_squared
    return theta_ref, orbital_rate


def reaction_wheel_torque(state: list[float], params: SatelliteParameters) -> float:
    _, _, _, _, theta, omega, wheel_momentum = state
    theta_ref, omega_ref = attitude_reference(state)
    pointing_error = _wrap_angle(theta_ref - theta)
    body_torque = clamp(
        params.attitude_kp * pointing_error + params.attitude_kd * (omega_ref - omega),
        -params.max_wheel_torque,
        params.max_wheel_torque,
    )

    max_wheel_momentum = params.wheel_inertia * params.max_wheel_speed
    wheel_torque = -body_torque
    if abs(wheel_momentum) >= max_wheel_momentum and wheel_torque * wheel_momentum > 0.0:
        wheel_torque = 0.0
    return wheel_torque


def _satellite_derivative(time: float, state: list[float], params: SatelliteParameters) -> list[float]:
    x, y, vx, vy, theta, omega, _wheel_momentum = state
    radius = math.hypot(x, y)
    gravity_scale = -params.earth_gravitational_parameter / radius**3
    ax = gravity_scale * x
    ay = gravity_scale * y

    thrust_accel = thrust_profile(time)
    if thrust_accel > 0.0:
        ax += thrust_accel * math.cos(theta)
        ay += thrust_accel * math.sin(theta)

    wheel_torque = reaction_wheel_torque(state, params)
    body_torque = -wheel_torque
    omega_dot = body_torque / params.body_inertia_z
    wheel_momentum_dot = wheel_torque

    return [vx, vy, ax, ay, omega, omega_dot, wheel_momentum_dot]


def _wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))
