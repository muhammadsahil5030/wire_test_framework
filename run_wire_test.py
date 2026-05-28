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
    exp_cfg = cfg["experiment"]

    # Test force gauge connection
    if args.test_force:
        force_gauge = PCEFBForceGauge(
            port=force_cfg["port"],
            baudrate=force_cfg["baudrate"],
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
        # Initialize instruments
        force_gauge = PCEFBForceGauge(
            port=force_cfg["port"],
            baudrate=force_cfg["baudrate"],
        )

        picomotor = PicomotorController(
            bridge_exe=motor_cfg["bridge_exe"]
        )

        # Run the experiment with proper resource management and error handling
        try:
            force_gauge.open()

            # The run_step_test function will handle the experiment logic, 
            # including moving the Picomotor and reading forces from the gauge. 
            # It will also save the results to a CSV file as specified in the configuration.
            run_step_test(
                force_gauge=force_gauge,
                picomotor=picomotor,
                axis=motor_cfg["axis"],
                step_size=exp_cfg["step_size"],
                n_steps=exp_cfg["n_steps"],
                settle_time_s=exp_cfg["settle_time_s"],
                force_timeout_s=exp_cfg["force_timeout_s"],
                output_file=exp_cfg["output_file"],
            )

        # Handle keyboard interrupt gracefully to allow the user to stop the experiment if needed
        except KeyboardInterrupt:
            print("\nExperiment interrupted by user.")

        finally:
            force_gauge.close()

        return
    
    # Plot the output CSV file from the experiment
    if args.plot:
        plot_wire_test_output(
            csv_file=exp_cfg["output_file"],
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