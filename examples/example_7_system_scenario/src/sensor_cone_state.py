from enum import Enum


class SensorConeState(str, Enum):
    CONNECTED = 'connected'
    DISCONNECTED = 'disconnected'
    NORMAL = 'normal'
    FALLEN = 'fallen'
    MOVING = 'moving'
    HITTING = 'hitting'
    RECONNECTED = 'reconnected'
