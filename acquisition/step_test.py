# acquisition/step_test.py
# High-level step-test experiment.
# Coordinates force gauge reading and Picomotor movement.

import csv
import time
from datetime import datetime
from pathlib import Path


def run_step_test(
    force_gauge,
    picomotor,
    axis: int,
    step_size: int,
    n_steps: int,
    settle_time_s: float,
    force_timeout_s: float,
    output_file: str,
    peak_measure_duration_s: float,
    peak_sampling_interval_s: float,
):
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Starting wire step-test experiment")
    print("=" * 70)
    print(f"Output file: {output_path.resolve()}")
    print(f"Axis: {axis}")
    print(f"Step size: {step_size}")
    print(f"Number of steps: {n_steps}")
    print(f"Settle time: {settle_time_s} s")
    print("=" * 70)

    initial_position = picomotor.get_position(axis)
    print(f"Initial Picomotor position: {initial_position} steps")

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "step_index",
            "time_s",
            "max_tension_N",
            "stable_tension_N",
        ])

        t0 = time.time()

        for step_index in range(1, n_steps + 1):
            print("-" * 70)
            print(f"Step {step_index}/{n_steps}")

            elapsed = time.time() - t0

            position_before = picomotor.get_position(axis)

            print(f"Before move: position = {position_before} steps")
            print(f"Moving axis {axis} by {step_size} steps...")

            move_data, move_text = picomotor.move_relative(axis, step_size)

            position_after = picomotor.get_position(axis)
            delta_position = position_after - position_before

            print(f"After move: position = {position_after} steps")
            print(f"Measured delta position: {delta_position} steps")

            # ------------------------------------------------------------
            # 1. Measure maximum tension immediately after the step
            # ------------------------------------------------------------
            print("Measuring maximum tension after step...")

            peak_start = time.time()
            max_tension = None

            while time.time() - peak_start < peak_measure_duration_s:
                force_value, force_unit, force_raw = force_gauge.read_force_once(
                    timeout_s=force_timeout_s
                )

                if force_value is not None:
                    if max_tension is None or force_value > max_tension:
                        max_tension = force_value

                time.sleep(peak_sampling_interval_s)

            print(f"Maximum tension after step: {max_tension} N")

            # ------------------------------------------------------------
            # 2. Wait for relaxation
            # ------------------------------------------------------------
            print(f"Waiting {settle_time_s} s for relaxation...")
            time.sleep(settle_time_s)

            # ------------------------------------------------------------
            # 3. Measure stable tension after relaxation
            # ------------------------------------------------------------
            stable_tension, stable_unit, stable_raw = force_gauge.read_force_once(
                timeout_s=force_timeout_s
            )

            elapsed = time.time() - t0

            print(f"Stable tension after relaxation: {stable_tension} N")

            writer.writerow([
                step_index,
                f"{elapsed:.6f}",
                max_tension if max_tension is not None else "",
                stable_tension if stable_tension is not None else "",
            ])

            f.flush()

    print("=" * 70)
    print("Experiment finished successfully.")
    print(f"CSV saved: {output_path.resolve()}")
    print("=" * 70)