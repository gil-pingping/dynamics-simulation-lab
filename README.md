# Dynamics Simulation Lab

차량, 매니퓰레이터, 휴머노이드뿐 아니라 드론과 위성까지 확장한 동역학 학습용 저장소다. 복잡한 프레임워크 없이 바로 실행할 수 있게 구성했고, 각 시뮬레이션은 `outputs/`에 CSV 결과를 남긴다.

## 포함된 시뮬레이션

- `src/dynamicslab/vehicle.py`: single-track bicycle vehicle dynamics와 lane change 시뮬레이션
- `src/dynamicslab/manipulator.py`: 2-link planar manipulator rigid-body dynamics와 PD + gravity compensation 제어
- `src/dynamicslab/humanoid.py`: LIPM-inspired 휴머노이드 CoM / ZMP 보행 시뮬레이션
- `src/dynamicslab/drone.py`: 2D quadrotor dynamics와 waypoint tracking 시뮬레이션
- `src/dynamicslab/satellite.py`: 2D two-body orbital dynamics와 low-thrust orbit raise 시뮬레이션
- `examples/drone_mission_demo.py`: 이륙, 전진, 착륙 구간을 포함한 드론 미션 예제
- `examples/satellite_orbit_demo.py`: 저추력으로 궤도 에너지를 올리는 위성 예제
- `examples/vehicle_lane_change_demo.py`: 차량 궤적과 steering 입력 예제
- `examples/manipulator_tracking_demo.py`: 조인트 추종과 end-effector 궤적 예제
- `examples/humanoid_walk_demo.py`: 발 디딤 계획에 따른 CoM 진행 예제
- `simulations/run_all.py`: 모든 데모 일괄 실행
- `tests/test_dynamics.py`: 기본 동작 검증

## 빠른 실행

```bash
python3 examples/vehicle_lane_change_demo.py
python3 examples/manipulator_tracking_demo.py
python3 examples/humanoid_walk_demo.py
python3 examples/drone_mission_demo.py
python3 examples/satellite_orbit_demo.py
python3 simulations/run_all.py
python3 -m unittest discover -s tests -v
```

선택적으로 플롯까지 저장하려면:

```bash
python3 -m pip install '.[plot]'
```

`matplotlib`가 설치되어 있으면 각 데모가 PNG 플롯도 함께 저장한다.

## 모델 개요

### 1. Vehicle Dynamics

차량은 single-track bicycle model로 표현했다.

- 상태: `x, y, yaw, vx, vy, yaw_rate`
- 입력: steering angle, longitudinal acceleration
- 힘 모델: front/rear tire cornering stiffness, drag, rolling resistance
- 시나리오: steering pulse를 이용한 lane change

결과는 `outputs/vehicle_lane_change.csv`에 저장된다.

![Vehicle lane change plot](https://raw.githubusercontent.com/gil-pingping/dynamics-simulation-lab/main/outputs/vehicle_lane_change.png)

### 2. Manipulator Dynamics

2-link planar manipulator의 rigid-body dynamics를 사용했다.

- 상태: `q1, q2, dq1, dq2`
- 동역학: 질량 행렬, 코리올리 항, 중력 항
- 제어기: PD + gravity compensation
- 시나리오: home pose에서 목표 joint configuration으로 smooth tracking

결과는 `outputs/manipulator_tracking.csv`에 저장된다.

![Manipulator tracking plot](https://raw.githubusercontent.com/gil-pingping/dynamics-simulation-lab/main/outputs/manipulator_tracking.png)

### 3. Humanoid Dynamics

휴머노이드는 full-body multibody 대신 LIPM-inspired CoM model로 단순화했다.

- 상태: `com_x, com_y, com_vx, com_vy`
- 입력: support foot 내부로 clamp된 ZMP
- 계획: alternating footstep sequence
- 제어기: CoM reference를 추종하는 ZMP controller

결과는 `outputs/humanoid_walk.csv`에 저장된다.

![Humanoid walking plot](https://raw.githubusercontent.com/gil-pingping/dynamics-simulation-lab/main/outputs/humanoid_walk.png)

### 4. Drone Dynamics

드론은 planar quadrotor model로 단순화했다.

- 상태: `x, z, vx, vz, theta, omega`
- 입력: collective thrust, pitch torque
- 제어기: outer-loop position tracking + inner-loop attitude stabilization
- 시나리오: 이륙 후 전진 비행, 고도 유지, 완만한 하강

결과는 `outputs/drone_mission.csv`에 저장된다.

![Drone mission plot](https://raw.githubusercontent.com/gil-pingping/dynamics-simulation-lab/main/outputs/drone_mission.png)

### 5. Satellite Dynamics

위성은 planar two-body orbital model에 저추력 가속을 추가한 형태로 구성했다.

- 상태: `x, y, vx, vy`
- 입력: velocity direction으로 가해지는 low thrust acceleration
- 동역학: central gravity + finite burn
- 시나리오: 400 km 근방 원형 궤도에서 에너지를 올려 더 높은 타원 궤도로 이동

결과는 `outputs/satellite_orbit_raise.csv`에 저장된다.

![Satellite orbit raise plot](https://raw.githubusercontent.com/gil-pingping/dynamics-simulation-lab/main/outputs/satellite_orbit_raise.png)

## 프로젝트 구조

```text
.
├── README.md
├── examples
│   ├── drone_mission_demo.py
│   ├── humanoid_walk_demo.py
│   ├── manipulator_tracking_demo.py
│   ├── satellite_orbit_demo.py
│   └── vehicle_lane_change_demo.py
├── outputs
├── pyproject.toml
├── simulations
│   └── run_all.py
├── src
│   └── dynamicslab
│       ├── __init__.py
│       ├── drone.py
│       ├── humanoid.py
│       ├── manipulator.py
│       ├── satellite.py
│       ├── utils.py
│       └── vehicle.py
└── tests
    └── test_dynamics.py
```

## 확장 아이디어

- nonlinear tire model과 combined slip vehicle dynamics
- inverse dynamics controller 또는 computed torque control
- full-body centroidal dynamics 혹은 MPC 기반 humanoid walking
- full 6-DoF quadrotor with motor mixing and wind disturbance
- coupled orbit-attitude satellite simulation with reaction wheel control
- notebook 기반 parameter sweep와 sensitivity analysis
