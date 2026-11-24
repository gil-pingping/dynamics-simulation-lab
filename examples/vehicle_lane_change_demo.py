from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import simulate_vehicle_lane_change
from dynamicslab.utils import write_dataclass_rows_csv


def main() -> None:
    output_dir = ROOT / "outputs"
    csv_path = output_dir / "vehicle_lane_change.csv"
    png_path = output_dir / "vehicle_lane_change.png"

    samples = simulate_vehicle_lane_change()
    write_dataclass_rows_csv(csv_path, samples)

    final = samples[-1]
    max_lateral = max(row.y for row in samples)
    min_lateral = min(row.y for row in samples)
    peak_lateral_accel = max(abs(row.lateral_accel) for row in samples)
    final_tracking_error = final.lateral_error
    print("Vehicle dynamics demo")
    print(f"- samples: {len(samples)}")
    print(f"- final position: x={final.x:.2f} m, y={final.y:.2f} m")
    print(f"- lateral envelope: [{min_lateral:.2f}, {max_lateral:.2f}] m")
    print(f"- final lateral tracking error: {final_tracking_error:.2f} m")
    print(f"- peak lateral acceleration: {peak_lateral_accel:.2f} m/s^2")
    print(f"- saved CSV: {csv_path}")

    if save_plot(samples, png_path):
        print(f"- saved plot: {png_path}")
    else:
        print("- plot skipped: matplotlib is not installed")


def save_plot(samples, path: Path) -> bool:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return False

    times = [row.time for row in samples]
    xs = [row.x for row in samples]
    ys = [row.y for row in samples]
    road_ys = [row.road_y for row in samples]
    steering = [row.steering * 180.0 / 3.141592653589793 for row in samples]
    steering_cmd = [row.steering_cmd * 180.0 / 3.141592653589793 for row in samples]
    speeds = [row.speed for row in samples]
    speed_refs = [row.speed_ref for row in samples]
    lateral_accel = [row.lateral_accel for row in samples]
    front_slip = [row.front_slip * 180.0 / 3.141592653589793 for row in samples]
    rear_slip = [row.rear_slip * 180.0 / 3.141592653589793 for row in samples]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes[0, 0].plot(xs, ys, linewidth=2.0, label="vehicle")
    axes[0, 0].plot(xs, road_ys, linewidth=1.8, linestyle="--", label="road center")
    axes[0, 0].set_title("Path tracking")
    axes[0, 0].set_xlabel("x (m)")
    axes[0, 0].set_ylabel("y (m)")
    axes[0, 0].grid(alpha=0.3)
    axes[0, 0].legend()

    axes[0, 1].plot(times, steering_cmd, linewidth=1.8, linestyle="--", label="command")
    axes[0, 1].plot(times, steering, linewidth=2.0, label="actual")
    axes[0, 1].set_title("Steering actuator")
    axes[0, 1].set_xlabel("time (s)")
    axes[0, 1].set_ylabel("steering (deg)")
    axes[0, 1].grid(alpha=0.3)
    axes[0, 1].legend()

    axes[1, 0].plot(times, speed_refs, linewidth=1.8, linestyle="--", label="reference")
    axes[1, 0].plot(times, speeds, linewidth=2.0, label="actual")
    axes[1, 0].set_title("Speed tracking")
    axes[1, 0].set_xlabel("time (s)")
    axes[1, 0].set_ylabel("speed (m/s)")
    axes[1, 0].grid(alpha=0.3)
    axes[1, 0].legend()

    axes[1, 1].plot(times, lateral_accel, linewidth=2.0, label="lateral accel")
    axes[1, 1].plot(times, front_slip, linewidth=1.6, linestyle="--", label="front slip")
    axes[1, 1].plot(times, rear_slip, linewidth=1.6, linestyle=":", label="rear slip")
    axes[1, 1].set_title("Handling response")
    axes[1, 1].set_xlabel("time (s)")
    axes[1, 1].set_ylabel("response")
    axes[1, 1].grid(alpha=0.3)
    axes[1, 1].legend()

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


if __name__ == "__main__":
    main()
