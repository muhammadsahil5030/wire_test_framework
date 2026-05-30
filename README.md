# Wire Test Framework

This framework controls a **PCE-FB force gauge** and a **Newport/New Focus Picomotor 8742** for wire tension tests. It supports two acquisition modes:

- **Static test**: step-by-step tension measurement with maximum and stable tension values.
- **Dynamic test**: continuous force measurement while the Picomotor moves at constant velocity.

The raw CSV files are intentionally kept clean so that further analysis frameworks can add derived columns later.

---

## 1. Project Structure

```text
wire_test_framework/
│
├── acquisition/
│   ├── step_test.py          # Static step-test acquisition
│   └── dynamic_test.py       # Dynamic constant-velocity acquisition
│
├── analysis/
│   └── quick_plot.py         # Quick plotting for static and dynamic CSV files
│
├── instruments/
│   ├── pce_fb_force_gauge.py # PCE-FB serial communication
│   └── picomotor_controller.py # Python wrapper for PicomotorBridge.exe
│
├── external/
│   └── newfocus/
│       └── PicomotorBridge.exe # Bridge to Newport/New Focus Picomotor API
│
├── data/
│   └── raw/                  # Raw CSV output files
│
├── output/
│   └── plots/                # Generated plots
│
├── config.yaml               # Main configuration file
├── run_wire_test.py          # Main command-line entry point
└── README.md
```

---

## 2. Configuration

All hardware and test settings are controlled from `config.yaml`.

Example:

```yaml
force_gauge:
  port: COM6
  baudrate: 115200
  timeout_s: 1.0
  default_unit: N

picomotor:
  bridge_exe: external/newfocus/PicomotorBridge.exe
  axis: 1

static_test:
  step_size: 10
  n_steps: 5
  settle_time_s: 0.5
  force_timeout_s: 2.0
  output_file: data/raw/static_wire_test.csv

  peak_measure_duration_s: 1.0
  peak_sampling_interval_s: 0.05

dynamic_test:
  velocity_steps_per_s: 667
  run_duration_s: 30.0
  direction: positive

  sampling_interval_s: 0.1
  force_timeout_s: 0.3

  max_duration_s: 120.0
  output_file: data/raw/dynamic_wire_test.csv
```

### Static-test parameters

| Parameter | Meaning |
|---|---|
| `step_size` | Picomotor relative step size for each static increment. |
| `n_steps` | Number of static loading steps. |
| `settle_time_s` | Waiting time after the peak search, allowing the wire tension to relax. |
| `force_timeout_s` | Timeout for one force reading from the PCE-FB. |
| `output_file` | Output CSV file for the static test. |
| `peak_measure_duration_s` | Time window immediately after each step to search for the maximum tension. |
| `peak_sampling_interval_s` | Delay between repeated force readings during the peak-search window. |

### Dynamic-test parameters

| Parameter | Meaning |
|---|---|
| `velocity_steps_per_s` | Picomotor velocity in steps per second. |
| `run_duration_s` | Duration of the dynamic test. |
| `direction` | Motion direction: `positive` or `negative`. |
| `sampling_interval_s` | Desired time spacing between saved force readings. |
| `force_timeout_s` | Timeout for one force reading from the PCE-FB. |
| `max_duration_s` | Safety maximum duration. |
| `output_file` | Output CSV file for the dynamic test. |

---

## 3. Raw CSV Formats

The raw CSV files store only the essential measured values.

### Static test CSV

```csv
step_index,time_s,max_tension_N,stable_tension_N
1,1.245672,0.185,0.162
2,2.893541,0.241,0.219
```

| Column | Meaning |
|---|---|
| `step_index` | Static loading step number. |
| `time_s` | Elapsed time from the beginning of the static test. |
| `max_tension_N` | Maximum tension measured immediately after the Picomotor step. |
| `stable_tension_N` | Stable tension measured after relaxation. |

### Dynamic test CSV

```csv
time_s,force_N
0.000123,0.000
0.101235,0.015
0.201422,0.031
```

| Column | Meaning |
|---|---|
| `time_s` | Elapsed time from the beginning of the dynamic test. |
| `force_N` | Force measured by the PCE-FB force gauge. |

---

## 4. Device Preparation

Before running a real test:

1. Connect the PCE-FB force gauge to the computer.
2. Check the correct COM port in Windows Device Manager.
3. Set the same COM port in `config.yaml`, for example `COM6`.
4. Put the PCE-FB in continuous transmission mode when using automatic acquisition.
5. Connect the Picomotor controller and close the official Picomotor software before using the Python framework.
6. Confirm that `PicomotorBridge.exe` exists at the path defined in `config.yaml`.

---

## 5. Command List

Run all commands from the main framework folder:

```powershell
cd E:\path\to\framework\wire_test_framework
```

### 5.1 List available serial ports

```powershell
python run_wire_test.py --list-ports
```

Use this command to identify the PCE-FB COM port.

### 5.2 Test the PCE-FB force gauge

```powershell
python run_wire_test.py --test-force
```

Expected behavior: the program opens the serial port, waits for a force message, prints the raw message, and prints the parsed force value.

### 5.3 Test the Picomotor controller

```powershell
python run_wire_test.py --test-picomotor
```

Expected behavior: the program discovers the Picomotor controller and prints the current position of the configured axis.

### 5.4 Zero the Picomotor axis

```powershell
python run_wire_test.py --zero-picomotor
```

Use this only when the current mechanical position should be treated as zero.

---

## 6. Running a Static Test

The static test performs small Picomotor steps. For each step, it measures:

1. Maximum tension immediately after the step.
2. Stable tension after relaxation.

Run:

```powershell
python run_wire_test.py --test_type static --run
```

The output CSV is defined in `config.yaml`:

```text
data/raw/static_wire_test.csv
```

Plot the static result:

```powershell
python run_wire_test.py --test_type static --plot
```

Expected plots:

```text
output/plots/static_tension_vs_step.png
output/plots/static_relaxation_drop_vs_step.png
```

---

## 7. Running a Dynamic Test

The dynamic test starts continuous Picomotor motion at constant velocity and records force as a function of time.

Run:

```powershell
python run_wire_test.py --test_type dynamic --run
```

The output CSV is defined in `config.yaml`:

```text
data/raw/dynamic_wire_test.csv
```

Plot the dynamic result:

```powershell
python run_wire_test.py --test_type dynamic --plot
```

Expected plot:

```text
output/plots/dynamic_force_vs_time.png
```

---

## 8. Recommended Test Workflow

### Static workflow

```powershell
cd E:\Education\PhD\Wire_test\Analysis_codes\serial_connection\wire_test_framework

python run_wire_test.py --list-ports
python run_wire_test.py --test-force
python run_wire_test.py --test-picomotor
python run_wire_test.py --zero-picomotor
python run_wire_test.py --test_type static --run
python run_wire_test.py --test_type static --plot
```

### Dynamic workflow

```powershell
cd E:\Education\PhD\Wire_test\Analysis_codes\serial_connection\wire_test_framework

python run_wire_test.py --list-ports
python run_wire_test.py --test-force
python run_wire_test.py --test-picomotor
python run_wire_test.py --zero-picomotor
python run_wire_test.py --test_type dynamic --run
python run_wire_test.py --test_type dynamic --plot
```

---

## 9. Safety Recommendations

Before testing a real wire:

- Use a very small `step_size` for static tests.
- Start with `n_steps: 1` to verify the full workflow.
- For dynamic tests, first use a short `run_duration_s`, for example `3.0` seconds.
- Confirm the Picomotor direction before loading the wire.
- Keep the force gauge within its rated force range.
- Stop the test immediately if the wire, fixtures, or force readings behave unexpectedly.

---

## 10. Git Workflow

Check modified files:

```powershell
git status
```

Add files:

```powershell
git add .
```

Commit changes:

```powershell
git commit -m "Prepare wire test framework for static and dynamic acquisition"
```

Push to the GitHub repository:

```powershell
git push origin master
```

If the repository uses `main` instead of `master`, use:

```powershell
git push origin main
```
