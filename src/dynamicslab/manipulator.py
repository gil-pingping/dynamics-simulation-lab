from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import rk4_step


@dataclass(slots=True)
class ManipulatorParameters:
    link1_length: float = 1.0
    link2_length: float = 0.8
    link1_com: float = 0.5
    link2_com: float = 0.4
    link1_mass: float = 2.2
    link2_mass: float = 1.5
    link1_inertia: float = 0.15
    link2_inertia: float = 0.08
    damping: float = 0.15
    gravity: float = 9.81
    kp1: float = 55.0
    kp2: float = 40.0
    kd1: float = 16.0
    kd2: float = 11.0


@dataclass(slots=True)
class ManipulatorSample:
    time: float
    q1: float
    q2: float
    dq1: float
    dq2: float
    ref_q1: float
    ref_q2: float
    tau1: float
    tau2: float
    end_effector_x: float
    end_effector_y: float


def simulate_manipulator_tracking(
    *,
    duration: float = 6.0,
    dt: float = 0.01,
    params: ManipulatorParameters | None = None,
) -> list[ManipulatorSample]:
    params = params or ManipulatorParameters()
    state = [0.0, 0.0, 0.0, 0.0]
    samples: list[ManipulatorSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        ref_q1, ref_q2, _, _ = reference_trajectory(time)
        tau1, tau2 = control_torque(time, state, params)
        end_effector_x, end_effector_y = end_effector_position(state[0], state[1], params)
        samples.append(
            ManipulatorSample(
                time=time,
                q1=state[0],
                q2=state[1],
                dq1=state[2],
                dq2=state[3],
                ref_q1=ref_q1,
                ref_q2=ref_q2,
                tau1=tau1,
                tau2=tau2,
                end_effector_x=end_effector_x,
                end_effector_y=end_effector_y,
            )
        )
        state = rk4_step(
            lambda current_time, current_state: _manipulator_derivative(current_time, current_state, params),
            time,
            state,
            dt,
        )
        time += dt

    return samples


def reference_trajectory(time: float) -> tuple[float, float, float, float]:
    start_q1, start_q2 = 0.0, 0.0
    goal_q1, goal_q2 = 0.85, -0.65

    if time <= 0.4:
        s = 0.0
        ds = 0.0
    elif time >= 2.8:
        s = 1.0
        ds = 0.0
    else:
        duration = 2.4
        tau = (time - 0.4) / duration
        s = tau * tau * (3.0 - 2.0 * tau)
        ds = (6.0 * tau * (1.0 - tau)) / duration

    ref_q1 = start_q1 + s * (goal_q1 - start_q1)
    ref_q2 = start_q2 + s * (goal_q2 - start_q2)
    ref_dq1 = ds * (goal_q1 - start_q1)
    ref_dq2 = ds * (goal_q2 - start_q2)
    return ref_q1, ref_q2, ref_dq1, ref_dq2


def control_torque(time: float, state: list[float], params: ManipulatorParameters) -> tuple[float, float]:
    q1, q2, dq1, dq2 = state
    ref_q1, ref_q2, ref_dq1, ref_dq2 = reference_trajectory(time)
    gravity_1, gravity_2 = gravity_vector(q1, q2, params)
    tau1 = params.kp1 * (ref_q1 - q1) + params.kd1 * (ref_dq1 - dq1) + gravity_1
    tau2 = params.kp2 * (ref_q2 - q2) + params.kd2 * (ref_dq2 - dq2) + gravity_2
    return tau1, tau2


def end_effector_position(q1: float, q2: float, params: ManipulatorParameters) -> tuple[float, float]:
    x = params.link1_length * math.cos(q1) + params.link2_length * math.cos(q1 + q2)
    y = params.link1_length * math.sin(q1) + params.link2_length * math.sin(q1 + q2)
    return x, y


def _manipulator_derivative(time: float, state: list[float], params: ManipulatorParameters) -> list[float]:
    q1, q2, dq1, dq2 = state
    tau1, tau2 = control_torque(time, state, params)
    m11, m12, m22 = mass_matrix_terms(q2, params)
    coriolis_1, coriolis_2 = coriolis_vector(q2, dq1, dq2, params)
    gravity_1, gravity_2 = gravity_vector(q1, q2, params)

    rhs1 = tau1 - coriolis_1 - gravity_1 - params.damping * dq1
    rhs2 = tau2 - coriolis_2 - gravity_2 - params.damping * dq2

    determinant = m11 * m22 - m12 * m12
    ddq1 = (m22 * rhs1 - m12 * rhs2) / determinant
    ddq2 = (-m12 * rhs1 + m11 * rhs2) / determinant

    return [dq1, dq2, ddq1, ddq2]


def mass_matrix_terms(q2: float, params: ManipulatorParameters) -> tuple[float, float, float]:
    cos_q2 = math.cos(q2)
    m11 = (
        params.link1_inertia
        + params.link2_inertia
        + params.link1_mass * params.link1_com**2
        + params.link2_mass
        * (params.link1_length**2 + params.link2_com**2 + 2.0 * params.link1_length * params.link2_com * cos_q2)
    )
    m12 = params.link2_inertia + params.link2_mass * (
        params.link2_com**2 + params.link1_length * params.link2_com * cos_q2
    )
    m22 = params.link2_inertia + params.link2_mass * params.link2_com**2
    return m11, m12, m22


def coriolis_vector(q2: float, dq1: float, dq2: float, params: ManipulatorParameters) -> tuple[float, float]:
    coupling = params.link2_mass * params.link1_length * params.link2_com * math.sin(q2)
    c1 = -coupling * (2.0 * dq1 * dq2 + dq2 * dq2)
    c2 = coupling * dq1 * dq1
    return c1, c2


def gravity_vector(q1: float, q2: float, params: ManipulatorParameters) -> tuple[float, float]:
    g1 = (
        (params.link1_mass * params.link1_com + params.link2_mass * params.link1_length)
        * params.gravity
        * math.cos(q1)
        + params.link2_mass * params.link2_com * params.gravity * math.cos(q1 + q2)
    )
    g2 = params.link2_mass * params.link2_com * params.gravity * math.cos(q1 + q2)
    return g1, g2
