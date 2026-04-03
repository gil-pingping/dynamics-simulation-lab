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
    print("Vehicle dynamics demo")
    print(f"- samples: {len(samples)}")
    print(f"- final position: x={final.x:.2f} m, y={final.y:.2f} m")
    print(f"- peak lateral displacement: {max_lateral:.2f} m")
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
    steer = [row.steering * 180.0 / 3.141592653589793 for row in samples]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(xs, ys, linewidth=2.0)
    axes[0].set_title("Vehicle path")
    axes[0].set_xlabel("x (m)")
    axes[0].set_ylabel("y (m)")
    axes[0].grid(alpha=0.3)

    axes[1].plot(times, steer, linewidth=2.0)
    axes[1].set_title("Steering input")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("steering (deg)")
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


if __name__ == "__main__":
    main()
