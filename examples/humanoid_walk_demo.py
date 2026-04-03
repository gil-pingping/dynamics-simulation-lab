from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import simulate_humanoid_walk
from dynamicslab.humanoid import footstep_plan
from dynamicslab.utils import write_dataclass_rows_csv


def main() -> None:
    output_dir = ROOT / "outputs"
    csv_path = output_dir / "humanoid_walk.csv"
    png_path = output_dir / "humanoid_walk.png"

    samples = simulate_humanoid_walk()
    write_dataclass_rows_csv(csv_path, samples)

    final = samples[-1]
    print("Humanoid dynamics demo")
    print(f"- samples: {len(samples)}")
    print(f"- final CoM: x={final.com_x:.3f} m, y={final.com_y:.3f} m")
    print(f"- support steps: {len(footstep_plan())}")
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
    com_x = [row.com_x for row in samples]
    com_y = [row.com_y for row in samples]
    zmp_x = [row.zmp_x for row in samples]
    zmp_y = [row.zmp_y for row in samples]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(com_x, com_y, label="CoM path", linewidth=2.0)
    axes[0].scatter(zmp_x[::20], zmp_y[::20], s=10, alpha=0.6, label="ZMP")
    axes[0].set_title("Humanoid CoM and ZMP")
    axes[0].set_xlabel("x (m)")
    axes[0].set_ylabel("y (m)")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(times, com_x, label="CoM x")
    axes[1].plot(times, zmp_x, label="ZMP x")
    axes[1].set_title("Forward progression")
    axes[1].set_xlabel("time (s)")
    axes[1].set_ylabel("x (m)")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


if __name__ == "__main__":
    main()
