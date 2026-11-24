from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import (
    simulate_ackermann_steering_course,
    simulate_articulated_vehicle_s_curve,
    simulate_double_track_obstacle_avoidance,
    simulate_drift_transition,
    simulate_full_vehicle_ride_and_handling,
    simulate_kinematic_bicycle_parking,
    simulate_offroad_traverse,
    simulate_skid_steer_maneuver,
)
from dynamicslab.utils import write_dataclass_rows_csv


def main() -> None:
    output_dir = ROOT / "outputs"
    simulations = [
        ("vehicle_kinematic_bicycle_parking.csv", "Kinematic bicycle", simulate_kinematic_bicycle_parking),
        ("vehicle_ackermann_steering_course.csv", "Ackermann steering", simulate_ackermann_steering_course),
        ("vehicle_double_track_obstacle_avoidance.csv", "Double-track", simulate_double_track_obstacle_avoidance),
        ("vehicle_skid_steer_maneuver.csv", "Skid-steer", simulate_skid_steer_maneuver),
        ("vehicle_articulated_s_curve.csv", "Articulated vehicle", simulate_articulated_vehicle_s_curve),
        ("vehicle_drift_transition.csv", "Drift / high-slip", simulate_drift_transition),
        ("vehicle_offroad_traverse.csv", "Off-road", simulate_offroad_traverse),
        ("vehicle_full_vehicle_handling.csv", "Full vehicle", simulate_full_vehicle_ride_and_handling),
    ]

    print("Vehicle model suite")
    for file_name, label, simulation in simulations:
        samples = simulation()
        path = output_dir / file_name
        write_dataclass_rows_csv(path, samples)
        final = samples[-1]
        x = getattr(final, "x", 0.0)
        y = getattr(final, "y", 0.0)
        print(f"- {label}: {len(samples)} samples, final x={x:.2f} m, y={y:.2f} m, saved {path.name}")


if __name__ == "__main__":
    main()
