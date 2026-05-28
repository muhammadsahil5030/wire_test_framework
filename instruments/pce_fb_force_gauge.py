# instruments/pce_fb_force_gauge.py
# PCE-FB force gauge interface.
# Responsible only for serial connection and force reading.

import re
import time
import serial
import serial.tools.list_ports


class PCEFBForceGauge:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    @staticmethod
    def list_ports():
        ports = list(serial.tools.list_ports.comports())

        print("\nDetected serial ports:")
        if not ports:
            print("  No serial ports found.")
        else:
            for p in ports:
                print(f"  {p.device:10s} | {p.description}")
        print()

    @staticmethod
    def parse_force(raw_text: str):
        text = raw_text.strip()
        text = text.replace(",", ".")

        number_match = re.search(r"[-+]?\s*\d+(?:\.\d+)?", text)

        if not number_match:
            return None, ""

        number_string = number_match.group(0).replace(" ", "")

        try:
            value = float(number_string)
        except ValueError:
            return None, ""

        unit_match = re.search(
            r"(kgf|lbf|ozf|N|kg|lb|oz|g)",
            text,
            re.IGNORECASE,
        )

        unit = unit_match.group(1) if unit_match else ""

        return value, unit

    def open(self):
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )

        time.sleep(1.0)
        print(f"PCE-FB opened on {self.port} at {self.baudrate} baud.")

    def close(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()
            print("PCE-FB serial port closed.")

    def read_raw_message(self):
        if self.ser is None:
            raise RuntimeError("PCE-FB serial port is not open.")

        data = self.ser.readline()

        if data:
            return data.decode(errors="ignore").strip()

        data = self.ser.read(16)

        if data:
            return data.decode(errors="ignore").strip()

        return ""

    def read_force_once(self, timeout_s: float = 2.0):
        start = time.time()

        while time.time() - start < timeout_s:
            raw = self.read_raw_message()

            if not raw:
                continue

            value, unit = self.parse_force(raw)

            return value, unit, raw

        return None, "", ""

    def test_connection(self, timeout_s: float = 10.0):
        print(f"Testing PCE-FB on {self.port} at {self.baudrate} baud...")
        print("Waiting for data. If not in CONTIN. mode, press PRINT.\n")

        start = time.time()

        while time.time() - start < timeout_s:
            value, unit, raw = self.read_force_once(timeout_s=1.0)

            if raw:
                print(f"Received raw data: {repr(raw)}")
                print(f"Parsed force: {value} {unit}")
                print("PCE-FB connection test PASSED.")
                return True

        print("PCE-FB connection test FAILED.")
        return False