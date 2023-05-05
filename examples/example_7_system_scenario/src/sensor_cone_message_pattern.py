from enum import Enum

class SensorConeMessagePattern(str, Enum):
    STARTUP_MESSAGE = r"Startup ([0-9A-F]{32})\n"
    ACCELERATION_MESSAGE = r"\d+ Acceleration ([0-9A-F]{32}) X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)\n"
    WORKING_MESSAGE = r"Working ([0-9A-F]{32})\n"
    STABLE_MESSAGE = r"Stable ([0-9A-F]{32}) X: (-?\d+\.\d+) Y: (-?\d+\.\d+) Z: (-?\d+\.\d+)\n"
