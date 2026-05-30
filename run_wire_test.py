# @author: Muhammad Saiel
# @date: 2024-06-01
# Wire-test framework: PCE-FB force gauge + Picomotor 8742
# This script serves as the main entry point for the wire-test framework. It provides command-line options to:
# - List available serial ports for the force gauge.
# - Test the connection to the PCE-FB force gauge.
# - Test the Picomotor bridge discovery and position reading.
# - Zero the Picomotor axis.
# - Run the step-test experiment.
# - Plot the output CSV file from the experiment.
# run_wire_test.py
# Main entry point for the wire-test framework.

# import standard libraries
import argparse
import yaml

from instruments.pce_fb_force_gauge import PCEFBForceGauge
from instruments.picomotor_controller import PicomotorController
from acquisition.step_test import run_step_test
from acquisition.dynamic_test import run_dynamic_test
from analysis.quick_plot import plot_wire_test_output

# Load configuration from YAML file
def load_config(config_file: str):
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Main function to parse command-line arguments and execute the appropriate actions
def main():
    parser = argparse.ArgumentParser(
        description="Wire-test framework: PCE-FB force gauge + Picomotor 8742"
    )

    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML configuration file. Default: config.yaml",
    )

    parser.add_argument(
        "--list-ports",
        action="store_true",
        help="List available serial ports and exit.",
    )

    parser.add_argument(
        "--test-force",
        action="store_true",
        help="Test PCE-FB force gauge connection and exit.",
    )

    parser.add_argument(
        "--test-picomotor",
        action="store_true",
        help="Test Picomotor bridge discovery and position reading and exit.",
    )

    parser.add_argument(
        "--zero-picomotor",
        action="store_true",
        help="Set current Picomotor axis position to zero and exit.",
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Run the step-test experiment.",
    )
    parser.add_argument(
        "--test_type",
        choices=["static", "dynamic"],
        default="static",
        help="Type of test to run: static or dynamic. Default: static.",
    )

    parser.add_argument(
    "--plot",
    action="store_true",
    help="Plot the output CSV file defined in config.yaml.",
    )

    args = parser.parse_args()

    # Handle command-line options
    if args.list_ports:
        PCEFBForceGauge.list_ports()
        return

    # Load configuration from YAML file
    cfg = load_config(args.config)

    # Extract relevant sections from the configuration
    force_cfg = cfg["force_gauge"]
    motor_cfg = cfg["picomotor"]
    
    static_cfg = cfg.get("static_test", {})
    dynamic_cfg = cfg.get("dynamic_test", {})

    # Test force gauge connection
    if args.test_force:
        force_gauge = PCEFBForceGauge(
            port=force_cfg["port"],
            baudrate=force_cfg["baudrate"],
            timeout=force_cfg.get("timeout_s", 1.0),
        )

        try:
            force_gauge.open()
            force_gauge.test_connection()
        finally:
            force_gauge.close()

        return

    # Test Picomotor bridge discovery and position reading
    if args.test_picomotor:
        picomotor = PicomotorController(
            bridge_exe=motor_cfg["bridge_exe"]
        )

        print("Testing Picomotor discovery...")
        print(picomotor.discover())

        axis = motor_cfg["axis"]
        position = picomotor.get_position(axis)
        print(f"Axis {axis} position: {position} steps")

        return

    # Zero Picomotor axis
    if args.zero_picomotor:
        picomotor = PicomotorController(
            bridge_exe=motor_cfg["bridge_exe"]
        )

        axis = motor_cfg["axis"]
        print(f"Zeroing Picomotor axis {axis}...")
        print(picomotor.zero(axis))

        return

    # Run the step-test experiment
    if args.run:
        force_gauge = PCEFBForceGauge(
            port=force_cfg["port"],
            baudrate=force_cfg["baudrate"],
            timeout=force_cfg.get("timeout_s", 1.0),
        )

        picomotor = PicomotorController(
            bridge_exe=motor_cfg["bridge_exe"]
        )

        try:
            force_gauge.open()

            if args.test_type == "static":
                static_cfg = cfg["static_test"]

                run_step_test(
                    force_gauge=force_gauge,
                    picomotor=picomotor,
                    axis=motor_cfg["axis"],
                    step_size=static_cfg["step_size"],
                    n_steps=static_cfg["n_steps"],
                    settle_time_s=static_cfg["settle_time_s"],
                    force_timeout_s=static_cfg["force_timeout_s"],
                    output_file=static_cfg["output_file"],
                    peak_measure_duration_s=static_cfg["peak_measure_duration_s"],
                    peak_sampling_interval_s=static_cfg["peak_sampling_interval_s"],
                )

            elif args.test_type == "dynamic":
                dynamic_cfg = cfg["dynamic_test"]

                run_dynamic_test(
                    force_gauge=force_gauge,
                    picomotor=picomotor,
                    axis=motor_cfg["axis"],
                    velocity_steps_per_s=dynamic_cfg["velocity_steps_per_s"],
                    #acceleration_steps_per_s2=dynamic_cfg.get("acceleration_steps_per_s2", None),
                    #total_steps=dynamic_cfg["total_steps"],
                    direction=dynamic_cfg["direction"],
                    run_duration_s=dynamic_cfg["run_duration_s"],
                    sampling_interval_s=dynamic_cfg["sampling_interval_s"],
                    force_timeout_s=dynamic_cfg["force_timeout_s"],
                    #pre_motion_duration_s=dynamic_cfg.get("pre_motion_duration_s", 1.0),
                    max_duration_s=dynamic_cfg["max_duration_s"],
                    output_file=dynamic_cfg["output_file"],
                )

        except KeyboardInterrupt:
            print("\nExperiment interrupted by user.")

            try:
                print("Trying to stop Picomotor after interruption...")
                picomotor.stop(motor_cfg["axis"])
            except Exception as exc:
                print("WARNING: Could not stop Picomotor normally.")
                print(exc)

        finally:
            force_gauge.close()

        return
    
    # Plot the output CSV file from the selected test type
    if args.plot:
        if args.test_type == "static":
            csv_file = static_cfg["output_file"]
        elif args.test_type == "dynamic":
            csv_file = dynamic_cfg["output_file"]
        else:
            raise ValueError(
                f"Unknown test_type: {args.test_type}. "
                "Allowed values are: static or dynamic."
            )

        plot_wire_test_output(
            csv_file=csv_file,
            output_dir="output/plots",
        )
        return
        
    # If no valid options were provided, print the help message
    parser.print_help()

# Entry point of the script
if __name__ == "__main__":
    main()

# This script provides a flexible command-line interface for testing and running the wire-test framework.
# It allows users to easily test their hardware connections, run experiments, and visualize results without modifying the code.
# End of run_wire_test.py