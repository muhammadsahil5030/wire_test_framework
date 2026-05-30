# acquisition/dynamic_test.py
# Dynamic wire-test experiment.
#
# Correct procedure:
#   1. Confirm Picomotor setup before motion
#   2. Prepare CSV before motion
#   3. Clear old dynamometer serial buffer before motion
#   4. Start Picomotor motion
#   5. Start force acquisition immediately
#   6. Save only fresh force readings during motion
#   7. Stop after selected run duration

import csv
import time
from datetime import datetime
from pathlib import Path


def run_dynamic_test(
    force_gauge,
    picomotor,
    axis: int,
    velocity_steps_per_s: int,
    direction: str,
    run_duration_s: float,
    sampling_interval_s: float,
    force_timeout_s: float,
    max_duration_s: float,
    output_file: str,
):
    """
    Run a clean time-based dynamic wire test.

    Data taking is NOT controlled by motor steps.

    Logic:
        setup everything first
        clear old PCE-FB serial data
        start motor
        immediately start force acquisition
        save force data to CSV
        stop after run_duration_s
    """

    if axis not in (1, 2, 3, 4):
        raise ValueError("Axis must be 1, 2, 3, or 4.")

    if velocity_steps_per_s <= 0:
        raise ValueError("velocity_steps_per_s must be positive.")

    if direction not in ("positive", "negative"):
        raise ValueError("direction must be 'positive' or 'negative'.")

    if run_duration_s <= 0:
        raise ValueError("run_duration_s must be positive.")

    if sampling_interval_s <= 0:
        raise ValueError("sampling_interval_s must be positive.")

    if max_duration_s <= 0:
        raise ValueError("max_duration_s must be positive.")

    if run_duration_s > max_duration_s:
        raise ValueError("run_duration_s cannot be larger than max_duration_s.")

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Starting dynamic wire-test experiment")
    print("=" * 70)
    print(f"Output file: {output_path.resolve()}")
    print(f"Axis: {axis}")
    print(f"Velocity: {velocity_steps_per_s} steps/s")
    print(f"Direction: {direction}")
    print(f"Run duration: {run_duration_s} s")
    print(f"Sampling interval: {sampling_interval_s} s")
    print(f"Force timeout: {force_timeout_s} s")
    print(f"Maximum duration: {max_duration_s} s")
    print("=" * 70)

    # ------------------------------------------------------------
    # 1. Setup phase: no motor motion yet
    # ------------------------------------------------------------

    print("Checking Picomotor position before motion...")
    start_position = picomotor.get_position(axis)
    print(f"Initial Picomotor position: {start_position} steps")

    print(f"Setting Picomotor velocity to {velocity_steps_per_s} steps/s...")
    data, text = picomotor.set_velocity(axis, velocity_steps_per_s)
    print(text)

    current_velocity = picomotor.get_velocity(axis)
    print(f"Confirmed Picomotor velocity: {current_velocity} steps/s")

    print("Preparing CSV file before motor starts...")

    motion_started = False

    with open(output_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "time_s",
            "force_N",
        ])
        f.flush()

        print("CSV file ready.")

        print("Clearing old dynamometer serial buffer before run...")
        if force_gauge.ser is not None and force_gauge.ser.is_open:
            force_gauge.ser.reset_input_buffer()
        print("Old dynamometer serial data cleared.")

        print("Setup confirmed.")
        print("Motor and force acquisition will now start.")

        # ------------------------------------------------------------
        # 2. Run phase: motor and force acquisition start here
        # ------------------------------------------------------------

        try:
            if direction == "positive":
                print("Starting positive Picomotor motion...")
                data, text = picomotor.jog_positive(axis)
            else:
                print("Starting negative Picomotor motion...")
                data, text = picomotor.jog_negative(axis)

            print(text)
            motion_started = True

            # Timing starts immediately after the motor command returns
            t0 = time.time()
            last_sample_time = -sampling_interval_s
            sample = 0

            print("Motor started. Force acquisition started.")

            while True:
                now = time.time()
                elapsed = now - t0

                if elapsed >= run_duration_s:
                    print("Requested run duration reached.")
                    break

                if elapsed >= max_duration_s:
                    print("WARNING: Maximum duration reached.")
                    break

                if elapsed - last_sample_time < sampling_interval_s:
                    time.sleep(0.001)
                    continue

                last_sample_time = elapsed
                sample += 1

                # Read force from dynamometer
                force_value, force_unit, force_raw = force_gauge.read_force_once(
                    timeout_s=force_timeout_s
                )

                read_time = time.time()
                elapsed_read = read_time - t0

                computer_datetime = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                )[:-3]

                writer.writerow([
                    f"{elapsed_read:.6f}",
                    force_value if force_value is not None else "",
                ])
                f.flush()

                print(
                    f"{sample:6d}  "
                    f"t = {elapsed_read:9.4f} s  "
                    f"F = {force_value} {force_unit}  "
                    f"raw = {repr(force_raw)}"
                )

        except KeyboardInterrupt:
            print("\nDynamic test interrupted by user.")

        finally:
            if motion_started:
                print("Stopping Picomotor...")
                try:
                    data, text = picomotor.stop(axis)
                    print(text)
                except Exception as exc:
                    print("WARNING: Normal stop failed.")
                    print(exc)
                    print("Trying emergency abort...")
                    try:
                        data, text = picomotor.abort(axis)
                        print(text)
                    except Exception as exc2:
                        print("ERROR: Emergency abort also failed.")
                        print(exc2)

    final_position = picomotor.get_position(axis)

    print("=" * 70)
    print("Dynamic experiment finished.")
    print(f"Initial position: {start_position} steps")
    print(f"Final position:   {final_position} steps")
    print(f"CSV saved: {output_path.resolve()}")
    print("=" * 70)