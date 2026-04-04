from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import rk4_step


@dataclass(slots=True)
class SatelliteParameters:
    earth_gravitational_parameter: float = 3.986004418e14
    earth_radius: float = 6_371_000.0
    initial_altitude: float = 400_000.0
    thrust_acceleration: float = 0.08


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


def simulate_satellite_orbit_raise(
    *,
    duration: float = 10_800.0,
    dt: float = 5.0,
    params: SatelliteParameters | None = None,
) -> list[SatelliteSample]:
    params = params or SatelliteParameters()
    initial_radius = params.earth_radius + params.initial_altitude
    circular_speed = math.sqrt(params.earth_gravitational_parameter / initial_radius)

    state = [initial_radius, 0.0, 0.0, circular_speed]
    samples: list[SatelliteSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        thrust_accel = thrust_profile(time)
        radius = math.hypot(state[0], state[1])
        speed = math.hypot(state[2], state[3])
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


def _satellite_derivative(time: float, state: list[float], params: SatelliteParameters) -> list[float]:
    x, y, vx, vy = state
    radius = math.hypot(x, y)
    gravity_scale = -params.earth_gravitational_parameter / radius**3
    ax = gravity_scale * x
    ay = gravity_scale * y

    thrust_accel = thrust_profile(time)
    speed = math.hypot(vx, vy)
    if thrust_accel > 0.0 and speed > 1e-9:
        ax += thrust_accel * vx / speed
        ay += thrust_accel * vy / speed

    return [vx, vy, ax, ay]
