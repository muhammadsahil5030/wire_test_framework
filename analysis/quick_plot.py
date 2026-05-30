# analysis/quick_plot.py
# Quick plotting tools for wire-test output CSV files.
#
# Supports:
#   1. Dynamic test CSV:
#        time_s, force_N
#
#   2. Static test CSV:
#        step_index, time_s, max_tension_N, stable_tension_N

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def plot_wire_test_output(csv_file: str, output_dir: str = "output/plots"):
    csv_path = Path(csv_file)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    print("Loaded CSV file:")
    print(csv_path.resolve())
    print()
    print("Columns:")
    print(df.columns.tolist())
    print()

    # Convert all columns to numeric where possible.
    # This keeps the plotting safe even if empty strings exist.
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # ------------------------------------------------------------
    # Case 1: Dynamic test
    # Expected columns:
    #   time_s, force_N
    # ------------------------------------------------------------
    if "time_s" in df.columns and "force_N" in df.columns:
        plt.figure(figsize=(8, 5))
        plt.plot(df["time_s"], df["force_N"], marker="o")
        plt.xlabel("Time [s]")
        plt.ylabel("Force [N]")
        plt.title("Dynamic wire test: force vs time")
        plt.grid(True)
        plt.tight_layout()

        out_file = output_path / "dynamic_force_vs_time.png"
        plt.savefig(out_file, dpi=300)
        plt.close()

        print(f"Saved: {out_file.resolve()}")

    # ------------------------------------------------------------
    # Case 2: Static test
    # Expected columns:
    #   step_index, time_s, max_tension_N, stable_tension_N
    # ------------------------------------------------------------
    if (
        "step_index" in df.columns
        and "max_tension_N" in df.columns
        and "stable_tension_N" in df.columns
    ):
        # Plot max and stable tension vs step index
        plt.figure(figsize=(8, 5))
        plt.plot(
            df["step_index"],
            df["max_tension_N"],
            marker="o",
            label="Maximum tension",
        )
        plt.plot(
            df["step_index"],
            df["stable_tension_N"],
            marker="s",
            label="Stable tension after relaxation",
        )
        plt.xlabel("Step index")
        plt.ylabel("Tension [N]")
        plt.title("Static wire test: maximum and stable tension")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        out_file = output_path / "static_tension_vs_step.png"
        plt.savefig(out_file, dpi=300)
        plt.close()

        print(f"Saved: {out_file.resolve()}")

        # Plot relaxation drop per step
        df["relaxation_drop_N"] = df["max_tension_N"] - df["stable_tension_N"]

        plt.figure(figsize=(8, 5))
        plt.plot(
            df["step_index"],
            df["relaxation_drop_N"],
            marker="o",
        )
        plt.xlabel("Step index")
        plt.ylabel("Relaxation drop [N]")
        plt.title("Static wire test: tension drop after relaxation")
        plt.grid(True)
        plt.tight_layout()

        out_file = output_path / "static_relaxation_drop_vs_step.png"
        plt.savefig(out_file, dpi=300)
        plt.close()

        print(f"Saved: {out_file.resolve()}")

    print()
    print("Quick plotting finished.")