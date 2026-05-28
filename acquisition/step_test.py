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
            "computer_datetime",
            "elapsed_time_s",
            "axis",
            "commanded_step_size",
            "position_before_steps",
            "position_after_steps",
            "delta_position_steps",
            "force_before",
            "force_before_unit",
            "force_before_raw",
            "force_after",
            "force_after_unit",
            "force_after_raw",
        ])

        t0 = time.time()

        for step_index in range(1, n_steps + 1):
            print("-" * 70)
            print(f"Step {step_index}/{n_steps}")

            elapsed = time.time() - t0
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

            position_before = picomotor.get_position(axis)
            force_before, unit_before, raw_before = force_gauge.read_force_once(
                timeout_s=force_timeout_s
            )

            print(
                f"Before move: position = {position_before} steps, "
                f"force = {force_before} {unit_before}"
            )

            print(f"Moving axis {axis} by {step_size} steps...")
            move_data, move_text = picomotor.move_relative(axis, step_size)

            time.sleep(settle_time_s)

            position_after = picomotor.get_position(axis)
            force_after, unit_after, raw_after = force_gauge.read_force_once(
                timeout_s=force_timeout_s
            )

            delta_position = position_after - position_before

            print(
                f"After move:  position = {position_after} steps, "
                f"force = {force_after} {unit_after}"
            )
            print(f"Measured delta position: {delta_position} steps")

            writer.writerow([
                step_index,
                now,
                f"{elapsed:.6f}",
                axis,
                step_size,
                position_before,
                position_after,
                delta_position,
                force_before if force_before is not None else "",
                unit_before,
                raw_before,
                force_after if force_after is not None else "",
                unit_after,
                raw_after,
            ])

            f.flush()

    print("=" * 70)
    print("Experiment finished successfully.")
    print(f"CSV saved: {output_path.resolve()}")
    print("=" * 70)