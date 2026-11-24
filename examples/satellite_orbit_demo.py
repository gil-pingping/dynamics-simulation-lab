from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import simulate_satellite_orbit_raise
from dynamicslab.satellite import SatelliteParameters
from dynamicslab.utils import write_dataclass_rows_csv


def main() -> None:
    output_dir = ROOT / "outputs"
    csv_path = output_dir / "satellite_orbit_raise.csv"
    png_path = output_dir / "satellite_orbit_raise.png"

    samples = simulate_satellite_orbit_raise()
    write_dataclass_rows_csv(csv_path, samples)

    params = SatelliteParameters()
    final = samples[-1]
    peak_altitude = max(row.altitude for row in samples)
    peak_wheel_speed = max(abs(row.wheel_speed) for row in samples)
    peak_pointing_error = max(abs(row.pointing_error_deg) for row in samples)
    print("Satellite dynamics demo")
    print(f"- samples: {len(samples)}")
    print(f"- initial altitude: {params.initial_altitude / 1000.0:.1f} km")
    print(f"- final altitude: {final.altitude / 1000.0:.1f} km")
    print(f"- peak altitude: {peak_altitude / 1000.0:.1f} km")
    print(f"- final pointing error: {final.pointing_error_deg:.2f} deg")
    print(f"- peak pointing error: {peak_pointing_error:.2f} deg")
    print(f"- peak wheel speed: {peak_wheel_speed:.2f} rad/s")
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

    earth_radius_km = SatelliteParameters().earth_radius / 1000.0
    xs = [row.x / 1000.0 for row in samples]
    ys = [row.y / 1000.0 for row in samples]
    times = [row.time / 3600.0 for row in samples]
    altitudes = [row.altitude / 1000.0 for row in samples]
    pointing_errors = [row.pointing_error_deg for row in samples]
    wheel_speeds = [row.wheel_speed for row in samples]

    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes[0, 0].plot(xs, ys, linewidth=2.0)
    earth = plt.Circle((0.0, 0.0), earth_radius_km, color="tab:blue", alpha=0.2)
    axes[0, 0].add_patch(earth)
    axes[0, 0].set_title("Orbital trajectory")
    axes[0, 0].set_xlabel("x (km)")
    axes[0, 0].set_ylabel("y (km)")
    axes[0, 0].axis("equal")
    axes[0, 0].grid(alpha=0.3)

    axes[0, 1].plot(times, altitudes, linewidth=2.0)
    axes[0, 1].set_title("Altitude history")
    axes[0, 1].set_xlabel("time (hr)")
    axes[0, 1].set_ylabel("altitude (km)")
    axes[0, 1].grid(alpha=0.3)

    axes[1, 0].plot(times, pointing_errors, linewidth=2.0, color="tab:orange")
    axes[1, 0].set_title("Pointing error")
    axes[1, 0].set_xlabel("time (hr)")
    axes[1, 0].set_ylabel("error (deg)")
    axes[1, 0].grid(alpha=0.3)

    axes[1, 1].plot(times, wheel_speeds, linewidth=2.0, color="tab:green")
    axes[1, 1].set_title("Reaction wheel speed")
    axes[1, 1].set_xlabel("time (hr)")
    axes[1, 1].set_ylabel("wheel speed (rad/s)")
    axes[1, 1].grid(alpha=0.3)

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140)
    plt.close(fig)
    return True


if __name__ == "__main__":
    main()
