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
    def _parse_key_values(text: str):
        data = {}

        for line in text.splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()

        return data

    def discover(self):
        return self._run(["discover"])

    def get_position(self, axis: int):
        text = self._run(["position", axis])
        data = self._parse_key_values(text)

        if "POSITION" not in data:
            raise RuntimeError(
                "Could not find POSITION in PicomotorBridge output:\n"
                + text
            )

        return int(data["POSITION"])

    def zero(self, axis: int):
        return self._run(["zero", axis])

    def move_relative(self, axis: int, steps: int, timeout_ms: int = 30000):
        text = self._run(["move", axis, steps, timeout_ms])
        data = self._parse_key_values(text)

        return data, text