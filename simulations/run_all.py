from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    scripts = [
        ROOT / "examples" / "vehicle_lane_change_demo.py",
        ROOT / "examples" / "manipulator_tracking_demo.py",
        ROOT / "examples" / "humanoid_walk_demo.py",
    ]

    for script in scripts:
        print(f"== Running {script.relative_to(ROOT)} ==", flush=True)
        subprocess.run([sys.executable, str(script)], check=True)
        print()

    print(f"Simulation outputs are available under {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
