from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import simulate_manipulator_tracking
from dynamicslab.utils import write_dataclass_rows_csv


def main() -> None:
    output_dir = ROOT / "outputs"
    csv_path = output_dir / "manipulator_tracking.csv"
    png_path = output_dir / "manipulator_tracking.png"

    samples = simulate_manipulator_tracking()
    write_dataclass_rows_csv(csv_path, samples)

    final = samples[-1]
    print("Manipulator dynamics demo")
    print(f"- samples: {len(samples)}")
    print(f"- final joint state: q1={final.q1:.3f} rad, q2={final.q2:.3f} rad")
    print(f"- final reference: q1={final.ref_q1:.3f} rad, q2={final.ref_q2:.3f} rad")
    print(f"- end effector: x={final.end_effector_x:.3f} m, y={final.end_effector_y:.3f} m")
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
    q1 = [row.q1 for row in samples]
    q2 = [row.q2 for row in samples]
    ref_q1 = [row.ref_q1 for row in samples]
    ref_q2 = [row.ref_q2 for row in samples]
    xs = [row.end_effector_x for row in samples]
    ys = [row.end_effector_y for row in samples]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(times, q1, label="q1")
    axes[0].plot(times, ref_q1, "--", label="ref q1")
    axes[0].plot(times, q2, label="q2")
    axes[0].plot(times, ref_q2, "--", label="ref q2")
    axes[0].set_title("Joint tracking")
    axes[0].set_xlabel("time (s)")
    axes[0].set_ylabel("angle (rad)")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(xs, ys, linewidth=2.0)
    axes[1].scatter([xs[0], xs[-1]], [ys[0], ys[-1]], s=30)
    axes[1].set_title("End effector path")
    axes[1].set_xlabel("x (m)")
    axes[1].set_ylabel("y (m)")
    axes[1].grid(alpha=0.3)
    axes[1].axis("equal")

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


if __name__ == "__main__":
    main()
