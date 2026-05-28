# Wire-Test Framework

Control framework for a wire-tension test using:

- PCE-FB force gauge / dynamometer
- Newport/New Focus Picomotor Model 8742
- CSV logging
- quick plotting of force and Picomotor-position data

The framework is designed so that device-specific code, experiment logic, plotting, and user configuration are kept separate.

---

## 1. Purpose

The goal of this framework is to perform a controlled wire-test experiment.

For the current implemented **static step-test**, the program does the following:

1. Opens the PCE-FB force gauge serial connection.
2. Connects to the Picomotor through `PicomotorBridge.exe`.
3. Reads the initial Picomotor position.
4. For each movement step:
   - reads the force before movement,
   - moves the Picomotor by a configured number of steps,
   - waits for mechanical settling,
   - reads the force after movement,
   - saves force, position, time, and raw serial data to a CSV file.
5. Optionally produces quick plots from the output CSV file.

---

## 2. Expected folder structure

The recommended folder structure is:

```text
wire_test_framework/
|
|-- README.md
|-- run_wire_test.py
|-- config.yaml
|
|-- instruments/
|   |-- __init__.py
|   |-- pce_fb_force_gauge.py
|   |-- picomotor_controller.py
|
|-- acquisition/
|   |-- __init__.py
|   |-- step_test.py
|
|-- analysis/
|   |-- __init__.py
|   |-- quick_plot.py
|
|-- external/
|   |-- newfocus/
|       |-- PicomotorBridge.exe
|       |-- PicomotorBridge.cs
|       |-- CmdLib.dll
|       |-- CmdLib8742.dll
|       |-- DeviceIOLib.dll
|       |-- NpEthernet.dll
|       |-- NpSerial.dll
|       |-- UsbDllWrap.dll
|
|-- data/
|   |-- raw/
|
|-- output/
    |-- plots/
```

The files `__init__.py` can be empty. They are recommended because they make the folders importable Python packages.

To create the missing `__init__.py` files in PowerShell:

```powershell
New-Item -ItemType File instruments\__init__.py
New-Item -ItemType File acquisition\__init__.py
New-Item -ItemType File analysis\__init__.py
```

If the files already exist, PowerShell may print an error saying the file already exists. That is fine.

---

## 3. Main files and responsibilities

### `run_wire_test.py`

Main entry point of the framework.

It provides command-line options to:

- list available serial ports,
- test the PCE-FB force gauge,
- test the Picomotor bridge,
- zero the Picomotor axis,
- run the static step-test,
- plot the output CSV file.

### `config.yaml`

Central user configuration file.

It contains:

- PCE-FB port and baudrate,
- Picomotor bridge path and axis,
- selected test mode,
- static-test settings,
- dynamic-test placeholder settings,
- safety settings.

### `instruments/pce_fb_force_gauge.py`

Device-specific interface for the PCE-FB force gauge.

It handles:

- serial-port opening,
- serial-port closing,
- raw message reading,
- force-value parsing,
- connection testing.

### `instruments/picomotor_controller.py`

Python wrapper around `PicomotorBridge.exe`.

It handles:

- bridge execution through `subprocess.run`,
- Picomotor discovery,
- position reading,
- zeroing,
- relative movement.

### `acquisition/step_test.py`

High-level static step-test procedure.

It coordinates the PCE-FB force gauge and the Picomotor.

### `analysis/quick_plot.py`

Quick plotting module for the output CSV.

It creates:

- force-after-vs-step plot,
- position-after-vs-step plot,
- force-before/after-vs-step plot.

### `external/newfocus/PicomotorBridge.exe`

Small C# command-line bridge used to communicate with the Newport/New Focus Picomotor Model 8742 through the official DLLs.

---

## 4. Requirements

### 4.1 Python packages

Install the required packages:

```powershell
python -m pip install pyserial pyyaml pandas matplotlib
```

Check that the packages are available:

```powershell
python -c "import serial, yaml, pandas, matplotlib; print('Packages OK')"
```

Check Python version:

```powershell
python --version
```

### 4.2 Newport/New Focus DLLs

The Picomotor bridge requires the Newport/New Focus DLL files to be available in:

```text
external/newfocus/
```

At minimum, the folder should contain:

```text
PicomotorBridge.exe
CmdLib.dll
CmdLib8742.dll
DeviceIOLib.dll
NpEthernet.dll
NpSerial.dll
UsbDllWrap.dll
```

If the bridge cannot discover the controller, make sure the official Newport/New Focus Picomotor application is closed. Only one program should control the device at a time.

---

## 5. Configuration file

Open the configuration file:

```powershell
notepad config.yaml
```

Recommended current configuration:

```yaml
force_gauge:
  port: COM6
  baudrate: 115200
  timeout: 1.0
  default_unit: N

picomotor:
  bridge_exe: external/newfocus/PicomotorBridge.exe
  axis: 1

test_mode: static

static_test:
  step_size: 10
  n_steps: 5
  settle_time_s: 0.5
  force_timeout_s: 2.0
  use_timestamp_output: true
  output_file: data/raw/static_wire_test.csv

dynamic_test:
  total_steps: 500
  sampling_interval_s: 0.05
  force_timeout_s: 0.2
  use_timestamp_output: true
  output_file: data/raw/dynamic_wire_test.csv

safety:
  max_step_size: 100
  max_total_steps: 1000
  allowed_direction: both
  dry_run: false
```

At the moment, the implemented mode is:

```yaml
test_mode: static
```

The `dynamic_test` block is only a placeholder for future development. Dynamic mode is not yet implemented.

---

## 6. PCE-FB force gauge settings

The PCE-FB force gauge must use the same baudrate as `config.yaml`.

Example:

```yaml
force_gauge:
  baudrate: 115200
```

Recommended serial settings:

```text
Baudrate: same as config.yaml, usually 115200
Bits: 8-bit
Parity: none
Send mode: CONTIN. for continuous transmission
```

For continuous data logging, set the PCE-FB output/send mode to:

```text
CONTIN.
```

If the device is not in continuous mode, press the `PRINT` button on the PCE-FB to send one value manually.

The PCE-FB manual describes serial interface options such as baudrate, 8-bit data, no parity, and send modes including `NORMAL`, `NOSTB`, `AUTOSTB`, and `CONTIN.`.

---

## 7. Go to the framework folder

Open PowerShell and go to the main framework directory:

```powershell
cd "E:\Education\PhD\Wire_test\Analysis_codes\serial_connection\wire_test_framework"
```

Use the correct path on your computer. The folder should contain:

```text
run_wire_test.py
config.yaml
```

---

## 8. Command overview

The main command format is:

```powershell
python run_wire_test.py [OPTION]
```

Available options:

```text
--config CONFIG_FILE     Use a custom YAML configuration file
--list-ports            List available serial ports
--test-force            Test the PCE-FB force gauge
--test-picomotor        Test Picomotor discovery and position reading
--zero-picomotor        Set current Picomotor axis position to zero
--run                   Run the static step-test experiment
--plot                  Plot the output CSV file
```

Example using the default config:

```powershell
python run_wire_test.py --test-force
```

Example using a custom config file:

```powershell
python run_wire_test.py --config config.yaml --test-force
```

---

## 9. Step-by-step usage

### Step 1: List serial ports

Run:

```powershell
python run_wire_test.py --list-ports
```

Use this to identify the PCE-FB COM port.

Example output:

```text
Detected serial ports:
  COM6       | USB Serial Port
```

Then update `config.yaml`:

```yaml
force_gauge:
  port: COM6
```

---

### Step 2: Test the PCE-FB force gauge

Make sure:

- the PCE-FB is switched on,
- the cable is connected,
- the COM port in `config.yaml` is correct,
- the baudrate in the device and YAML file are the same,
- the device is in `CONTIN.` mode, or you press `PRINT` manually.

Run:

```powershell
python run_wire_test.py --test-force
```

Expected successful output:

```text
PCE-FB opened on COM6 at 115200 baud.
Testing PCE-FB on COM6 at 115200 baud...
Waiting for data. If not in CONTIN. mode, press PRINT.

Received raw data: '0.000'
Parsed force: 0.0 N
PCE-FB connection test PASSED.
PCE-FB serial port closed.
```

If no data is received, check:

- COM port,
- baudrate,
- cable,
- driver,
- PCE-FB send mode,
- whether another program is using the same COM port.

---

### Step 3: Test the Picomotor bridge directly

Before testing from Python, test the bridge executable directly.

Go to the bridge folder:

```powershell
cd external\newfocus
```

Discover the Picomotor controller:

```powershell
.\PicomotorBridge.exe discover
```

Read the current position of axis 1:

```powershell
.\PicomotorBridge.exe position 1
```

Move axis 1 by a very small number of steps:

```powershell
.\PicomotorBridge.exe move 1 10
```

Move back:

```powershell
.\PicomotorBridge.exe move 1 -10
```

Return to the main framework folder:

```powershell
cd ..\..
```

---

### Step 4: Test the Picomotor through the Python framework

Run:

```powershell
python run_wire_test.py --test-picomotor
```

This checks:

1. whether `PicomotorBridge.exe` can be executed,
2. whether the device can be discovered,
3. whether the configured axis position can be read.

The axis is taken from `config.yaml`:

```yaml
picomotor:
  axis: 1
```

---

### Step 5: Zero the Picomotor position

Only do this when the mechanical position is safe and you want the current position to become zero.

Run:

```powershell
python run_wire_test.py --zero-picomotor
```

This calls:

```text
PicomotorBridge.exe zero <axis>
```

where `<axis>` is taken from `config.yaml`.

---

### Step 6: Run the static step-test

Check the static-test block in `config.yaml`:

```yaml
static_test:
  step_size: 10
  n_steps: 5
  settle_time_s: 0.5
  force_timeout_s: 2.0
  output_file: data/raw/static_wire_test.csv
```

Then run:

```powershell
python run_wire_test.py --run
```

During the run, the program will print the step number, position before movement, force before movement, position after movement, force after movement, and measured position change.

The CSV file is saved to the path configured here:

```yaml
output_file: data/raw/static_wire_test.csv
```

---

### Step 7: Plot the result

After a successful run, create quick plots:

```powershell
python run_wire_test.py --plot
```

Plots are saved in:

```text
output/plots/
```

Expected plot files:

```text
force_after_vs_step.png
position_after_vs_step.png
force_before_after_vs_step.png
```

---

## 10. Recommended safe full sequence

Use this sequence for a safe first test:

```powershell
cd "E:\Education\PhD\Wire_test\Analysis_codes\serial_connection\wire_test_framework"

python run_wire_test.py --list-ports
python run_wire_test.py --test-force

cd external\newfocus
.\PicomotorBridge.exe discover
.\PicomotorBridge.exe position 1
.\PicomotorBridge.exe move 1 10
.\PicomotorBridge.exe move 1 -10
cd ..\..

python run_wire_test.py --test-picomotor
python run_wire_test.py --zero-picomotor
python run_wire_test.py --run
python run_wire_test.py --plot
```

Do not start with large movement steps. Always begin with small values such as:

```yaml
step_size: 10
n_steps: 5
```

---

## 11. Direct PicomotorBridge commands

These commands are useful for low-level testing and debugging.

Go to:

```powershell
cd external\newfocus
```

Discover device:

```powershell
.\PicomotorBridge.exe discover
```

Print available methods from the Newport/New Focus DLL:

```powershell
.\PicomotorBridge.exe methods
```

Read position:

```powershell
.\PicomotorBridge.exe position 1
```

Set current position to zero:

```powershell
.\PicomotorBridge.exe zero 1
```

Move relative:

```powershell
.\PicomotorBridge.exe move 1 10
```

Move back:

```powershell
.\PicomotorBridge.exe move 1 -10
```

Get velocity:

```powershell
.\PicomotorBridge.exe get_velocity 1
```

Set velocity:

```powershell
.\PicomotorBridge.exe set_velocity 1 50
```

Get acceleration:

```powershell
.\PicomotorBridge.exe get_acceleration 1
```

Set acceleration:

```powershell
.\PicomotorBridge.exe set_acceleration 1 100
```

Start positive jog:

```powershell
.\PicomotorBridge.exe jog_positive 1
```

Start negative jog:

```powershell
.\PicomotorBridge.exe jog_negative 1
```

Stop motion:

```powershell
.\PicomotorBridge.exe stop 1
```

Abort motion:

```powershell
.\PicomotorBridge.exe abort 1
```

Return to the main framework folder:

```powershell
cd ..\..
```

---

## 12. Output CSV format

The static step-test output CSV contains the following columns:

```text
step_index
computer_datetime
elapsed_time_s
axis
commanded_step_size
position_before_steps
position_after_steps
delta_position_steps
force_before
force_before_unit
force_before_raw
force_after
force_after_unit
force_after_raw
```

Meaning of important columns:

| Column | Meaning |
|---|---|
| `step_index` | Current step number |
| `computer_datetime` | Computer timestamp when the step starts |
| `elapsed_time_s` | Elapsed time from start of run |
| `axis` | Picomotor axis number |
| `commanded_step_size` | Requested motor movement in steps |
| `position_before_steps` | Picomotor position before movement |
| `position_after_steps` | Picomotor position after movement |
| `delta_position_steps` | Measured motor-position change |
| `force_before` | Parsed force before movement |
| `force_before_unit` | Unit parsed from force-gauge message |
| `force_before_raw` | Raw PCE-FB serial message before movement |
| `force_after` | Parsed force after movement |
| `force_after_unit` | Unit parsed from force-gauge message |
| `force_after_raw` | Raw PCE-FB serial message after movement |

---

## 13. Safety notes

Before running a real wire test:

1. Start with a small step size.
2. Start with a small number of steps.
3. Confirm the motor direction before applying tension.
4. Confirm whether positive motor movement increases or decreases tension.
5. Keep the direct stop command ready.
6. Do not leave the test unattended.
7. Do not exceed the safe force range of the wire or the force gauge.
8. Do not rely on the overload margin of the force gauge.

Recommended first values:

```yaml
static_test:
  step_size: 10
  n_steps: 5
```

Emergency direct stop command:

```powershell
cd external\newfocus
.\PicomotorBridge.exe stop 1
```

Emergency abort command:

```powershell
.\PicomotorBridge.exe abort 1
```

The PCE-FB datasheet/manual indicates that the device has a maximum overload limit around 20% above the measuring range. This should be treated only as a protection limit, not as an operating region.

---

## 14. Common problems

### Problem: `ModuleNotFoundError: No module named 'instruments'`

Cause:

The script is probably not being run from the main framework folder, or the package marker files are missing.

Fix:

Run from the folder containing `run_wire_test.py`:

```powershell
cd "E:\Education\PhD\Wire_test\Analysis_codes\serial_connection\wire_test_framework"
```

Make sure these files exist:

```text
instruments/__init__.py
acquisition/__init__.py
analysis/__init__.py
```

---

### Problem: PCE-FB serial port opens but no data is received

Possible causes:

- wrong COM port,
- wrong baudrate,
- PCE-FB not in continuous send mode,
- `PRINT` was not pressed,
- cable or driver issue,
- another program is using the COM port.

Fix:

```powershell
python run_wire_test.py --list-ports
python run_wire_test.py --test-force
```

Check the PCE-FB interface settings and set send mode to `CONTIN.` if continuous transmission is needed.

---

### Problem: PicomotorBridge cannot discover the controller

Possible causes:

- controller is off,
- USB cable is disconnected,
- official Newport/New Focus software is open,
- required DLL files are missing,
- wrong bridge path in `config.yaml`.

Fix:

Close the official Picomotor application and run:

```powershell
cd external\newfocus
.\PicomotorBridge.exe discover
```

Check this path in `config.yaml`:

```yaml
picomotor:
  bridge_exe: external/newfocus/PicomotorBridge.exe
```

---

### Problem: `KeyError: 'experiment'`

Cause:

Older code may try to read:

```python
cfg["experiment"]
```

but the current config uses:

```yaml
test_mode: static
static_test:
```

Fix:

`run_wire_test.py` should select the experiment block using `test_mode`.

Expected logic:

```python
def select_experiment_config(cfg):
    test_mode = cfg.get("test_mode", "static").lower()

    if test_mode == "static":
        return cfg["static_test"]

    if test_mode == "dynamic":
        raise NotImplementedError(
            "Dynamic test mode is defined in config.yaml, "
            "but dynamic acquisition is not implemented yet."
        )

    raise ValueError(
        f"Unknown test_mode: {test_mode}. "
        "Allowed values are: static or dynamic."
    )
```

Then inside `main()`:

```python
cfg = load_config(args.config)

force_cfg = cfg["force_gauge"]
motor_cfg = cfg["picomotor"]
exp_cfg = select_experiment_config(cfg)
```

---

### Problem: Plot command fails

Possible causes:

- the experiment has not been run yet,
- the CSV file does not exist,
- the output path in `config.yaml` is wrong.

Fix:

First run:

```powershell
python run_wire_test.py --run
```

Then:

```powershell
python run_wire_test.py --plot
```

---

## 15. Development status

Implemented:

- PCE-FB serial connection,
- PCE-FB raw message parsing,
- Picomotor bridge wrapper,
- static step-test acquisition,
- CSV output,
- quick plotting.

Prepared but not yet fully implemented:

- `dynamic_test` configuration block,
- `safety` configuration block.

Recommended next improvements:

1. Enforce safety limits from the `safety:` block before moving the motor.
2. Add Python-level `stop()` and `abort()` methods to `PicomotorController`.
3. Add timestamped output filenames when `use_timestamp_output: true`.
4. Add dynamic acquisition mode.
5. Add persistent Picomotor connection if faster dynamic operation is needed.

---

## 16. Minimal command summary

From the main framework folder:

```powershell
python run_wire_test.py --list-ports
python run_wire_test.py --test-force
python run_wire_test.py --test-picomotor
python run_wire_test.py --zero-picomotor
python run_wire_test.py --run
python run_wire_test.py --plot
```

Direct Picomotor bridge test:

```powershell
cd external\newfocus
.\PicomotorBridge.exe discover
.\PicomotorBridge.exe position 1
.\PicomotorBridge.exe move 1 10
.\PicomotorBridge.exe move 1 -10
cd ..\..
```
