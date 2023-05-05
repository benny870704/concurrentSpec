import re
from math import sqrt, acos, pi
from .sensor_cone_message_pattern import SensorConeMessagePattern
from .sensor_cone_state import SensorConeState

messagePatterns = [SensorConeMessagePattern.ACCELERATION_MESSAGE, SensorConeMessagePattern.STABLE_MESSAGE, SensorConeMessagePattern.STARTUP_MESSAGE]

def hex_to_int(hexString: str):
    number = int(hexString, 16)
    if number >= 128:
        number -= 256
    return number

def decode_uuid_from_startup_message(startupMessage: str):
    matchObject = re.search(SensorConeMessagePattern.STARTUP_MESSAGE, startupMessage)
    return matchObject.group(1) if matchObject is not None else None

def decode_uuid_and_acceleration_from_stable_message(stableMessage: str, pattern = SensorConeMessagePattern.STABLE_MESSAGE):
    matchObject = re.search(pattern, stableMessage)
    return matchObject.group(1), (matchObject.group(2), matchObject.group(3), matchObject.group(4)) if matchObject is not None else None

def decode_uuid_and_acceleration_from_acceleration_message(accelerationMessage: str, pattern = SensorConeMessagePattern.ACCELERATION_MESSAGE):
    matchObject = re.search(pattern, accelerationMessage)
    return matchObject.group(1), (matchObject.group(2), matchObject.group(3), matchObject.group(4)) if matchObject is not None else None

def decode_uuid_from_working_message(workingMessage: str):
    matchObject = re.search(SensorConeMessagePattern.WORKING_MESSAGE, workingMessage)
    return matchObject.group(1) if matchObject is not None else None

def calculate_sensor_cone_angle(acceleration):
    x = float(acceleration[0])
    y = float(acceleration[1])
    z = float(acceleration[2])
    Xg = z / sqrt(x*x + y*y + z*z)
    
    return round((90 - (acos(Xg)*180.0)/pi), 2)

def calculate_sensor_cone_angle_from_acceleration_message(message):
    matchObject = re.search(SensorConeMessagePattern.ACCELERATION_MESSAGE, message)
    if matchObject is not None:
        (x, y, z) = (matchObject[2], matchObject[3], matchObject[4])
        x = float(x)
        y = float(y)
        z = float(z)
        Xg = z / sqrt(x*x + y*y + z*z)
        
        return round((90 - (acos(Xg)*180.0)/pi), 2)
    else: return 999.0

def calculate_sensor_cone_angle_from_message(message):
    for pattern in messagePatterns:
        matchObject = re.search(pattern, message)
        if matchObject is not None:
            (x, y, z) = (matchObject[2], matchObject[3], matchObject[4])
            break
    x = float(x)
    y = float(y)
    z = float(z)
    Xg = z / sqrt(x*x + y*y + z*z)
    
    return round((90 - (acos(Xg)*180.0)/pi), 2)

def verify_message_is_valid(message: str, message_pattern: SensorConeMessagePattern):
    return re.compile(message_pattern).match(message)

def verify_message_is_stable_message(message: str):
    return re.compile(SensorConeMessagePattern.STABLE_MESSAGE).match(message)

def verify_message_is_startup_message(message: str):
    return re.compile(SensorConeMessagePattern.STARTUP_MESSAGE).match(message)

def verify_message_is_acceleration_message(message: str):
    return re.compile(SensorConeMessagePattern.ACCELERATION_MESSAGE).match(message)

def verify_state_by_acceleration_message(accelerationMessage, state: SensorConeState):
    _, acceleration = decode_uuid_and_acceleration_from_acceleration_message(accelerationMessage)
    x = hex_to_int(acceleration[0])
    y = hex_to_int(acceleration[1])
    z = hex_to_int(acceleration[2])
    if state == SensorConeState.NORMAL:
        return (z > 0 and z * z > x * x + y * y)
    elif state == SensorConeState.FALLEN:
        return not (z > 0 and z * z > x * x + y * y)

def verify_state_by_sensor_cone_data(sensor_cone_data, state: SensorConeState):
    return sensor_cone_data["state"] == state

def verify_state_of_all_acceleration_messages(messages, state: SensorConeState):
    if not messages: return False
    for message in messages:
        if not verify_state_by_acceleration_message(message, state): return False
    return True

def generate_startup_message(uuid: str):
        startup_message = f'Startup {uuid}\n'
        return startup_message

def generate_acceleration_message(uuid: str, acceleration: tuple):
    acceleration_message = f'Acceleration {uuid} X: {acceleration[0]} Y: {acceleration[1]} Z: {acceleration[2]}\n'
    return acceleration_message

def generate_working_message(uuid: str):
    working_message = f'Working {uuid}\n'
    return working_message

def acceleration_is_in_error_range(acceleration_message: str, acceleration: tuple):
    actual_acceleration = transfer_acceleration_from_string_to_float(decode_uuid_and_acceleration_from_acceleration_message(acceleration_message)[1])
    expected_acceleration = transfer_acceleration_from_string_to_float(acceleration)
    
    for i in range(3):
        if (abs(expected_acceleration[i] - actual_acceleration[i] <= 0.1)):
            continue
        else:
            raise RuntimeError("acceleration not in the error range!")
    
    return True
    
def transfer_acceleration_from_string_to_float(acceleration: tuple):
    return (float(acceleration[0]), float(acceleration[1]), float(acceleration[2]))
    