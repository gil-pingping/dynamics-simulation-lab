from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import simulate_humanoid_walk, simulate_manipulator_tracking, simulate_vehicle_lane_change


class VehicleDynamicsTests(unittest.TestCase):
    def test_lane_change_creates_lateral_displacement(self) -> None:
        samples = simulate_vehicle_lane_change()
        self.assertGreater(samples[-1].x, 80.0)
        self.assertGreater(max(row.y for row in samples), 1.5)


class ManipulatorDynamicsTests(unittest.TestCase):
    def test_joint_controller_tracks_target(self) -> None:
        samples = simulate_manipulator_tracking()
        final = samples[-1]
        self.assertLess(abs(final.q1 - final.ref_q1), 0.12)
        self.assertLess(abs(final.q2 - final.ref_q2), 0.12)


class HumanoidDynamicsTests(unittest.TestCase):
    def test_com_moves_forward_without_large_lateral_drift(self) -> None:
        samples = simulate_humanoid_walk()
        final = samples[-1]
        self.assertGreater(final.com_x, 1.0)
        self.assertLess(max(abs(row.com_y) for row in samples), 0.25)


if __name__ == "__main__":
    unittest.main()
