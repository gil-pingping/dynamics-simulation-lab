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
    print("Manipulator dynamics demo (6-DOF)")
    print(f"- samples: {len(samples)}")
    print(f"- final joint state: q1={final.q1:.3f}, q2={final.q2:.3f}, q3={final.q3:.3f}, q4={final.q4:.3f}, q5={final.q5:.3f}, q6={final.q6:.3f} rad")
    print(f"- end effector: x={final.ee_x:.3f} m, y={final.ee_y:.3f} m, z={final.ee_z:.3f} m")
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
    q = [[getattr(row, f"q{i}") for row in samples] for i in range(1, 7)]
    xs = [row.ee_x for row in samples]
    ys = [row.ee_y for row in samples]
    zs = [row.ee_z for row in samples]

    fig = plt.figure(figsize=(12, 5))
    
    ax1 = fig.add_subplot(121)
    for i in range(6):
        ax1.plot(times, q[i], label=f"q{i+1}")
    ax1.set_title("Joint tracking (6-DOF)")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("angle (rad)")
    ax1.grid(alpha=0.3)
    ax1.legend()

    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot(xs, ys, zs, linewidth=2.0)
    ax2.scatter([xs[0], xs[-1]], [ys[0], ys[-1]], [zs[0], zs[-1]], s=30, color='r')
    ax2.set_title("End effector path (3D)")
    ax2.set_xlabel("x (m)")
    ax2.set_ylabel("y (m)")
    ax2.set_zlabel("z (m)")

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


if __name__ == "__main__":
    main()
