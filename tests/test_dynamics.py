from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dynamicslab import (
    simulate_ackermann_steering_course,
    simulate_articulated_vehicle_s_curve,
    simulate_double_track_obstacle_avoidance,
    simulate_drift_transition,
    simulate_drone_mission,
    simulate_full_vehicle_ride_and_handling,
    simulate_humanoid_walk,
    simulate_kinematic_bicycle_parking,
    simulate_manipulator_tracking,
    simulate_offroad_traverse,
    simulate_satellite_orbit_raise,
    simulate_skid_steer_maneuver,
    simulate_vehicle_lane_change,
)


class VehicleDynamicsTests(unittest.TestCase):
    def test_lane_change_creates_bidirectional_lateral_excursion(self) -> None:
        samples = simulate_vehicle_lane_change()
        self.assertGreater(samples[-1].x, 140.0)
        self.assertGreater(max(row.y for row in samples), 3.0)
        self.assertLess(min(row.y for row in samples), -2.0)

    def test_vehicle_recovers_to_reference_lane_with_bounded_response(self) -> None:
        samples = simulate_vehicle_lane_change()
        final = samples[-1]
        peak_lateral_accel = max(abs(row.lateral_accel) for row in samples)

        self.assertLess(abs(final.lateral_error), 0.6)
        self.assertAlmostEqual(final.speed, final.speed_ref, delta=1.0)
        self.assertGreater(peak_lateral_accel, 4.0)
        self.assertLess(peak_lateral_accel, 9.5)


class VehicleModelFamilyTests(unittest.TestCase):
    def test_kinematic_bicycle_parks_close_to_target_pose(self) -> None:
        samples = simulate_kinematic_bicycle_parking()
        final = samples[-1]

        self.assertLess(final.position_error, 0.2)
        self.assertLess(abs(final.speed), 0.1)

    def test_ackermann_model_shows_inner_outer_steering_difference(self) -> None:
        samples = simulate_ackermann_steering_course()
        max_asymmetry = max(abs(row.steering_left - row.steering_right) for row in samples)

        self.assertGreater(max(row.y for row in samples), 4.0)
        self.assertLess(min(row.y for row in samples), -4.0)
        self.assertGreater(max_asymmetry, 0.08)

    def test_double_track_model_exhibits_left_right_load_transfer(self) -> None:
        samples = simulate_double_track_obstacle_avoidance()
        max_front_split = max(abs(row.front_left_normal_load - row.front_right_normal_load) for row in samples)

        self.assertGreater(samples[-1].x, 120.0)
        self.assertGreater(max_front_split, 2_000.0)

    def test_skid_steer_can_pivot_and_reorient(self) -> None:
        samples = simulate_skid_steer_maneuver()
        peak_yaw = max(abs(row.yaw) for row in samples)

        self.assertGreater(peak_yaw, 2.0)
        self.assertGreater(max(abs(row.y) for row in samples), 20.0)

    def test_articulated_vehicle_develops_and_recovers_articulation(self) -> None:
        samples = simulate_articulated_vehicle_s_curve()
        final = samples[-1]
        peak_articulation = max(abs(row.articulation_angle) for row in samples)

        self.assertGreater(peak_articulation, 0.25)
        self.assertLess(abs(final.articulation_angle), 0.08)

    def test_drift_model_reaches_high_sideslip(self) -> None:
        samples = simulate_drift_transition()
        peak_sideslip = max(abs(row.sideslip_deg) for row in samples)

        self.assertGreater(peak_sideslip, 12.0)
        self.assertLess(peak_sideslip, 30.0)

    def test_offroad_model_encounters_variable_friction(self) -> None:
        samples = simulate_offroad_traverse()
        frictions = [row.local_friction for row in samples]

        self.assertGreater(samples[-1].x, 70.0)
        self.assertLess(min(frictions), max(frictions) - 0.15)

    def test_full_vehicle_model_generates_body_attitude_response(self) -> None:
        samples = simulate_full_vehicle_ride_and_handling()
        peak_roll = max(abs(row.roll_deg) for row in samples)
        peak_pitch = max(abs(row.pitch_deg) for row in samples)
        peak_wheel_speed = max(
            max(abs(row.wheel_speed_fl), abs(row.wheel_speed_fr), abs(row.wheel_speed_rl), abs(row.wheel_speed_rr))
            for row in samples
        )

        self.assertGreater(samples[-1].x, 100.0)
        self.assertGreater(peak_roll, 3.0)
        self.assertLess(peak_roll, 12.0)
        self.assertGreater(peak_pitch, 0.8)
        self.assertGreater(peak_wheel_speed, 30.0)


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


class DroneDynamicsTests(unittest.TestCase):
    def test_drone_reaches_reference_zone(self) -> None:
        samples = simulate_drone_mission()
        final = samples[-1]
        self.assertGreater(final.x, 5.7)
        self.assertAlmostEqual(final.z, 1.2, delta=0.12)
        self.assertLess(max(abs(row.theta) for row in samples), 0.6)


class SatelliteDynamicsTests(unittest.TestCase):
    def test_orbit_raise_increases_peak_altitude(self) -> None:
        samples = simulate_satellite_orbit_raise()
        initial_altitude = samples[0].altitude
        peak_altitude = max(row.altitude for row in samples)
        final_specific_energy = samples[-1].specific_energy
        initial_specific_energy = samples[0].specific_energy

        self.assertGreater(peak_altitude, initial_altitude + 200_000.0)
        self.assertGreater(final_specific_energy, initial_specific_energy)

    def test_reaction_wheel_tracks_velocity_pointing_during_burn(self) -> None:
        samples = simulate_satellite_orbit_raise()
        burn_samples = [row for row in samples if 900.0 <= row.time <= 2_400.0]
        peak_burn_error = max(abs(row.pointing_error_deg) for row in burn_samples)
        peak_wheel_speed = max(abs(row.wheel_speed) for row in samples)

        self.assertLess(peak_burn_error, 0.1)
        self.assertGreater(peak_wheel_speed, 0.5)


if __name__ == "__main__":
    unittest.main()
