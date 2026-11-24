from __future__ import annotations

from dataclasses import dataclass
import math

from .utils import rk4_step


@dataclass(slots=True)
class ManipulatorParameters:
    # 6-DOF Robot parameters (e.g., loosely based on a UR or industrial robot)
    # Link lengths (meters)
    l1: float = 0.4   # Base height
    l2: float = 0.6   # Upper arm
    l3: float = 0.5   # Forearm
    l4: float = 0.15  # Wrist 1
    l5: float = 0.15  # Wrist 2
    l6: float = 0.1   # Wrist 3 to end-effector
    
    # Decoupled dynamics parameters per joint (Inertia, Damping)
    inertias: tuple[float, float, float, float, float, float] = (0.5, 1.0, 0.8, 0.2, 0.2, 0.1)
    dampings: tuple[float, float, float, float, float, float] = (0.5, 1.0, 0.8, 0.2, 0.2, 0.1)
    
    # PD Controller gains per joint
    kp: tuple[float, float, float, float, float, float] = (100.0, 150.0, 120.0, 50.0, 50.0, 30.0)
    kd: tuple[float, float, float, float, float, float] = (20.0, 30.0, 24.0, 10.0, 10.0, 6.0)


@dataclass(slots=True)
class ManipulatorSample:
    time: float
    q1: float
    q2: float
    q3: float
    q4: float
    q5: float
    q6: float
    dq1: float
    dq2: float
    dq3: float
    dq4: float
    dq5: float
    dq6: float
    tau1: float
    tau2: float
    tau3: float
    tau4: float
    tau5: float
    tau6: float
    ee_x: float
    ee_y: float
    ee_z: float


def simulate_manipulator_tracking(
    *,
    duration: float = 8.0,
    dt: float = 0.01,
    params: ManipulatorParameters | None = None,
) -> list[ManipulatorSample]:
    params = params or ManipulatorParameters()
    # State: [q1..q6, dq1..dq6]
    state = [0.0] * 12
    samples: list[ManipulatorSample] = []
    time = 0.0
    steps = int(duration / dt)

    for _ in range(steps + 1):
        ref_q, ref_dq = reference_trajectory(time)
        tau = control_torque(time, state, params)
        ee_x, ee_y, ee_z = end_effector_position(state[:6], params)
        
        samples.append(
            ManipulatorSample(
                time=time,
                q1=state[0], q2=state[1], q3=state[2], q4=state[3], q5=state[4], q6=state[5],
                dq1=state[6], dq2=state[7], dq3=state[8], dq4=state[9], dq5=state[10], dq6=state[11],
                tau1=tau[0], tau2=tau[1], tau3=tau[2], tau4=tau[3], tau5=tau[4], tau6=tau[5],
                ee_x=ee_x, ee_y=ee_y, ee_z=ee_z,
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


def reference_trajectory(time: float) -> tuple[list[float], list[float]]:
    # 6-DOF target poses
    start_q = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    # Pick and place motion
    goal_q = [math.pi/2, -math.pi/4, math.pi/2, -math.pi/4, -math.pi/2, math.pi]

    if time <= 0.5:
        s = 0.0
        ds = 0.0
    elif time >= 4.5:
        s = 1.0
        ds = 0.0
    else:
        duration = 4.0
        tau = (time - 0.5) / duration
        # Smooth step (minimum jerk)
        s = tau * tau * (3.0 - 2.0 * tau)
        ds = (6.0 * tau * (1.0 - tau)) / duration

    ref_q = [start_q[i] + s * (goal_q[i] - start_q[i]) for i in range(6)]
    ref_dq = [ds * (goal_q[i] - start_q[i]) for i in range(6)]
    
    return ref_q, ref_dq


def control_torque(time: float, state: list[float], params: ManipulatorParameters) -> list[float]:
    q = state[:6]
    dq = state[6:]
    ref_q, ref_dq = reference_trajectory(time)
    
    tau = []
    for i in range(6):
        t = params.kp[i] * (ref_q[i] - q[i]) + params.kd[i] * (ref_dq[i] - dq[i])
        tau.append(t)
    return tau


def end_effector_position(q: list[float], params: ManipulatorParameters) -> tuple[float, float, float]:
    # Simplified Forward Kinematics (similar to UR structure)
    # q[0]: Base (Z-axis rotation)
    # q[1]: Shoulder (Y-axis rotation)
    # q[2]: Elbow (Y-axis rotation)
    # q[3]: Wrist 1 (Y-axis rotation)
    # q[4]: Wrist 2 (Z-axis rotation)
    # q[5]: Wrist 3 (Y-axis rotation)
    
    # Transformation matrices approach
    def rot_z(angle):
        c, s = math.cos(angle), math.sin(angle)
        return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        
    def rot_y(angle):
        c, s = math.cos(angle), math.sin(angle)
        return [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]
        
    def trans(dx, dy, dz):
        return [[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz], [0, 0, 0, 1]]
        
    def multiply(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

    # T01: Base
    T01 = multiply(rot_z(q[0]), trans(0, 0, params.l1))
    # T12: Shoulder
    T12 = multiply(rot_y(q[1]), trans(0, 0, params.l2))
    # T23: Elbow
    T23 = multiply(rot_y(q[2]), trans(0, 0, params.l3))
    # T34: Wrist 1
    T34 = multiply(rot_y(q[3]), trans(0, params.l4, 0))
    # T45: Wrist 2
    T45 = multiply(rot_z(q[4]), trans(0, 0, params.l5))
    # T56: Wrist 3 to EE
    T56 = multiply(rot_y(q[5]), trans(0, 0, params.l6))

    T = T01
    for m in [T12, T23, T34, T45, T56]:
        T = multiply(T, m)
        
    return T[0][3], T[1][3], T[2][3]


def _manipulator_derivative(time: float, state: list[float], params: ManipulatorParameters) -> list[float]:
    q = state[:6]
    dq = state[6:]
    tau = control_torque(time, state, params)
    
    # Decoupled dynamics: I * ddq + b * dq = tau
    ddq = []
    for i in range(6):
        accel = (tau[i] - params.dampings[i] * dq[i]) / params.inertias[i]
        ddq.append(accel)

    return dq + ddq
