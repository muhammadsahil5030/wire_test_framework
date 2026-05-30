# instruments/picomotor_controller.py
# Python wrapper for PicomotorBridge.exe.
# Responsible only for Picomotor discovery, position, zero, and movement.

import subprocess
from pathlib import Path

class PicomotorController:
    def __init__(self, bridge_exe: str):
        self.bridge_exe = Path(bridge_exe)

        if not self.bridge_exe.exists():
            raise FileNotFoundError(
                f"PicomotorBridge.exe not found:\n{self.bridge_exe}"
            )

    # Run the PicomotorBridge.exe with the given arguments and return the output.
    def _run(self, args, timeout_s: float = 60.0):
        command = [str(self.bridge_exe)] + [str(a) for a in args]

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )

        if completed.returncode != 0:
            raise RuntimeError(
                "PicomotorBridge failed.\n"
                f"Command: {' '.join(command)}\n"
                f"Return code: {completed.returncode}\n"
                f"STDOUT:\n{completed.stdout}\n"
                f"STDERR:\n{completed.stderr}"
            )

        return completed.stdout

    @staticmethod
    # Parse key=value lines from PicomotorBridge output into a dictionary.
    def _parse_key_values(text: str):
        data = {}

        for line in text.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()

        return data

    # PicomotorBridge commands:
    def discover(self):
        return self._run(["discover"])

    # Get the current position of one axis in steps.
    def get_position(self, axis: int):
        text = self._run(["position", axis])
        data = self._parse_key_values(text)

        if "POSITION" not in data:
            raise RuntimeError(
                "Could not find POSITION in PicomotorBridge output:\n"
                + text
            )

        return int(data["POSITION"])

    # Zero the current position of one axis.
    def zero(self, axis: int):
        return self._run(["zero", axis])

    # Move one axis by a relative number of steps.
    # Positive steps move in the positive direction, negative steps move in the negative direction.
    def move_relative(self, axis: int, steps: int, timeout_ms: int = 30000):
        text = self._run(["move", axis, steps, timeout_ms])
        data = self._parse_key_values(text)

        return data, text
    
    # Move one axis to an absolute position in steps.
    def get_velocity(self, axis: int):
        """
        Read the current Picomotor velocity for one axis.

        Returns:
            velocity in steps/s
        """
        text = self._run(["get_velocity", axis])
        data = self._parse_key_values(text)

        if "VELOCITY" not in data:
            raise RuntimeError(
                "Could not find VELOCITY in PicomotorBridge output:\n"
                + text
            )

        return int(data["VELOCITY"])

    # Set Picomotor velocity for one axis.
    def set_velocity(self, axis: int, velocity_steps_per_s: int):
        """
        Set Picomotor velocity for one axis.

        Parameters:
            axis: motor axis, usually 1
            velocity_steps_per_s: velocity in steps/s
        """
        text = self._run(["set_velocity", axis, velocity_steps_per_s])
        data = self._parse_key_values(text)

        return data, text

    # Move one axis to an absolute position in steps.
    def get_acceleration(self, axis: int):
        """
        Read the current Picomotor acceleration for one axis.

        Returns:
            acceleration in steps/s^2
        """
        text = self._run(["get_acceleration", axis])
        data = self._parse_key_values(text)

        if "ACCELERATION" not in data:
            raise RuntimeError(
                "Could not find ACCELERATION in PicomotorBridge output:\n"
                + text
            )

        return int(data["ACCELERATION"])

    # Set Picomotor acceleration for one axis.
    def set_acceleration(self, axis: int, acceleration_steps_per_s2: int):
        """
        Set Picomotor acceleration for one axis.

        Parameters:
            axis: motor axis, usually 1
            acceleration_steps_per_s2: acceleration in steps/s^2
        """
        text = self._run(["set_acceleration", axis, acceleration_steps_per_s2])
        data = self._parse_key_values(text)

        return data, text

    # Move one axis to an absolute position in steps.
    def jog_positive(self, axis: int):
        """
        Start continuous positive motion.
        The motor keeps moving until stop() or abort() is called.
        """
        text = self._run(["jog_positive", axis])
        data = self._parse_key_values(text)

        return data, text

    # Move one axis to an absolute position in steps.
    def jog_negative(self, axis: int):
        """
        Start continuous negative motion.
        The motor keeps moving until stop() or abort() is called.
        """
        text = self._run(["jog_negative", axis])
        data = self._parse_key_values(text)

        return data, text

    # Stop continuous motion started by jog_positive() or jog_negative().
    def stop(self, axis: int):
        """
        Stop Picomotor motion normally.
        """
        text = self._run(["stop", axis])
        data = self._parse_key_values(text)

        return data, text

    # Emergency stop / abort Picomotor motion.
    def abort(self, axis: int):
        """
        Emergency stop / abort Picomotor motion.
        """
        text = self._run(["abort", axis])
        data = self._parse_key_values(text)

        return data, text