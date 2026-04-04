from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import simulate_drone_mission
from dynamicslab.utils import write_dataclass_rows_csv


def main() -> None:
    output_dir = ROOT / "outputs"
    csv_path = output_dir / "drone_mission.csv"
    png_path = output_dir / "drone_mission.png"

    samples = simulate_drone_mission()
    write_dataclass_rows_csv(csv_path, samples)

    final = samples[-1]
    peak_altitude = max(row.z for row in samples)
    max_tilt_deg = max(abs(row.theta) for row in samples) * 180.0 / 3.141592653589793
    print("Drone dynamics demo")
    print(f"- samples: {len(samples)}")
    print(f"- final position: x={final.x:.2f} m, z={final.z:.2f} m")
    print(f"- peak altitude: {peak_altitude:.2f} m")
    print(f"- max pitch magnitude: {max_tilt_deg:.2f} deg")
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
    zs = [row.z for row in samples]
    ref_xs = [row.ref_x for row in samples]
    ref_zs = [row.ref_z for row in samples]
    thetas = [row.theta * 180.0 / 3.141592653589793 for row in samples]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(xs, zs, label="Drone path", linewidth=2.0)
    axes[0].plot(ref_xs, ref_zs, "--", label="Reference path", linewidth=1.5)
    axes[0].set_title("Planar drone trajectory")
    axes[0].set_xlabel("x (m)")
    axes[0].set_ylabel("z (m)")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(times, thetas, linewidth=2.0)
    axes[1].set_title("Pitch response")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("pitch (deg)")
    axes[1].grid(alpha=0.3)

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


if __name__ == "__main__":
    main()
