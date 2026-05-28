# analysis/quick_plot.py
# Quick plotting tools for wire-test output CSV files.

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

    # Convert important columns to numeric safely
    numeric_columns = [
        "step_index",
        "elapsed_time_s",
        "position_before_steps",
        "position_after_steps",
        "delta_position_steps",
        "force_before",
        "force_after",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ------------------------------------------------------------
    # Plot 1: Force after each step
    # ------------------------------------------------------------
    if "step_index" in df.columns and "force_after" in df.columns:
        plt.figure(figsize=(8, 5))
        plt.plot(df["step_index"], df["force_after"], marker="o")
        plt.xlabel("Step index")
        plt.ylabel("Force after move")
        plt.title("Force after each Picomotor step")
        plt.grid(True)
        plt.tight_layout()

        out_file = output_path / "force_after_vs_step.png"
        plt.savefig(out_file, dpi=300)
        plt.close()

        print(f"Saved: {out_file.resolve()}")

    # ------------------------------------------------------------
    # Plot 2: Picomotor position after each step
    # ------------------------------------------------------------
    if "step_index" in df.columns and "position_after_steps" in df.columns:
        plt.figure(figsize=(8, 5))
        plt.plot(df["step_index"], df["position_after_steps"], marker="o")
        plt.xlabel("Step index")
        plt.ylabel("Picomotor position [steps]")
        plt.title("Picomotor position after each step")
        plt.grid(True)
        plt.tight_layout()

        out_file = output_path / "position_after_vs_step.png"
        plt.savefig(out_file, dpi=300)
        plt.close()

        print(f"Saved: {out_file.resolve()}")

    # ------------------------------------------------------------
    # Plot 3: Force before and after
    # ------------------------------------------------------------
    if (
        "step_index" in df.columns
        and "force_before" in df.columns
        and "force_after" in df.columns
    ):
        plt.figure(figsize=(8, 5))
        plt.plot(df["step_index"], df["force_before"], marker="o", label="Before move")
        plt.plot(df["step_index"], df["force_after"], marker="s", label="After move")
        plt.xlabel("Step index")
        plt.ylabel("Force")
        plt.title("Force before and after Picomotor movement")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        out_file = output_path / "force_before_after_vs_step.png"
        plt.savefig(out_file, dpi=300)
        plt.close()

        print(f"Saved: {out_file.resolve()}")

    print()
    print("Quick plotting finished.")