from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import clamp, rk4_step


@dataclass(slots=True)
class HumanoidParameters:
    com_height: float = 0.85
    gravity: float = 9.81
    step_duration: float = 0.55
    foot_half_length: float = 0.09
    foot_half_width: float = 0.05
    kp: float = 4.0
    kd: float = 2.4
    max_acceleration: float = 2.5


@dataclass(slots=True)
class HumanoidSample:
    time: float
    com_x: float
    com_y: float
    com_vx: float
    com_vy: float
    zmp_x: float
    zmp_y: float
    support_x: float
    support_y: float
    support_index: int


def simulate_humanoid_walk(
    *,
    dt: float = 0.01,
    params: HumanoidParameters | None = None,
) -> list[HumanoidSample]:
    params = params or HumanoidParameters()
    footsteps = footstep_plan()
    duration = params.step_duration * len(footsteps)
    omega = math.sqrt(params.gravity / params.com_height)

    state = [-0.03, 0.0, 0.0, 0.0]
    samples: list[HumanoidSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        support_index, support_x, support_y = support_foot(time, footsteps, params.step_duration)
        _, _, zmp_x, zmp_y = com_controller(time, state, footsteps, params, omega)
        samples.append(
            HumanoidSample(
                time=time,
                com_x=state[0],
                com_y=state[1],
                com_vx=state[2],
                com_vy=state[3],
                zmp_x=zmp_x,
                zmp_y=zmp_y,
                support_x=support_x,
                support_y=support_y,
                support_index=support_index,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _humanoid_derivative(
                current_time,
                current_state,
                footsteps,
                params,
                omega,
            ),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def footstep_plan() -> list[tuple[float, float]]:
    return [
        (0.00, 0.10),
        (0.28, -0.10),
        (0.56, 0.10),
        (0.84, -0.10),
        (1.12, 0.10),
        (1.40, -0.10),
        (1.68, 0.10),
    ]


def support_foot(time: float, footsteps: list[tuple[float, float]], step_duration: float) -> tuple[int, float, float]:
    index = min(int(time / step_duration), len(footsteps) - 1)
    support_x, support_y = footsteps[index]
    return index, support_x, support_y


def com_controller(
    time: float,
    state: list[float],
    footsteps: list[tuple[float, float]],
    params: HumanoidParameters,
    omega: float,
) -> tuple[float, float, float, float]:
    com_x, com_y, com_vx, com_vy = state
    support_index, support_x, support_y = support_foot(time, footsteps, params.step_duration)
    next_index = min(support_index + 1, len(footsteps) - 1)
    next_x, next_y = footsteps[next_index]
    phase = (time - support_index * params.step_duration) / params.step_duration
    phase = clamp(phase, 0.0, 1.0)

    ref_x = support_x + 0.85 * phase * (next_x - support_x)
    ref_y = 0.4 * support_y + 0.1 * phase * (next_y - support_y)
    ref_vx = 0.85 * (next_x - support_x) / params.step_duration if next_index != support_index else 0.0
    ref_vy = 0.1 * (next_y - support_y) / params.step_duration if next_index != support_index else 0.0

    desired_acc_x = clamp(
        params.kp * (ref_x - com_x) + params.kd * (ref_vx - com_vx),
        -params.max_acceleration,
        params.max_acceleration,
    )
    desired_acc_y = clamp(
        params.kp * (ref_y - com_y) + params.kd * (ref_vy - com_vy),
        -params.max_acceleration,
        params.max_acceleration,
    )

    zmp_x = clamp(
        com_x - desired_acc_x / (omega * omega),
        support_x - params.foot_half_length,
        support_x + params.foot_half_length,
    )
    zmp_y = clamp(
        com_y - desired_acc_y / (omega * omega),
        support_y - params.foot_half_width,
        support_y + params.foot_half_width,
    )
    return desired_acc_x, desired_acc_y, zmp_x, zmp_y


def _humanoid_derivative(
    time: float,
    state: list[float],
    footsteps: list[tuple[float, float]],
    params: HumanoidParameters,
    omega: float,
) -> list[float]:
    del omega

    _, _, com_vx, com_vy = state
    com_ax, com_ay, _, _ = com_controller(time, state, footsteps, params, math.sqrt(params.gravity / params.com_height))
    return [com_vx, com_vy, com_ax, com_ay]
