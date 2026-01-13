from cereal import car
from opendbc.can.packer import CANPacker
from selfdrive.car.scooter.values import CAR, DBC

# This is the file that will live at:
# /data/openpilot/selfdrive/car/scooter/carcontroller.py

class CarController:
  def __init__(self, dbc_name, CP, VM):
    self.CP = CP
    # The packer uses the DBC file to convert human-readable signal names
    # and values into the correct 8-byte CAN data payload.
    self.packer = CANPacker(DBC[CP.carFingerprint]['pt'])

  def update(self, CC, CS):
    # CC (CarControl) contains the high-level commands from openpilot's planner.
    #   - CC.enabled: True if openpilot is active.
    #   - CC.actuators: Contains the desired steering, throttle, and brake values.

    # CS (CarState) contains the current state of the vehicle (not used here but required).

    # Create a list to hold the CAN messages we want to send.
    can_sends = []

    # 1. Create the SYSTEM_STATE heartbeat message.
    # This is the most important message for safety. The Arduino will use this
    # to know that openpilot is alive and in control.
    # The CONTROLS_ENABLED signal is a 1-bit flag.
    can_sends.append(self.packer.make_can_msg("SYSTEM_STATE", 0, {"CONTROLS_ENABLED": CC.enabled}))

    # 2. Create the STEERING_COMMAND message.
    # CC.actuators.steer is a float from -1.0 (full left) to 1.0 (full right).
    # We convert this to our signal's -128 to 127 range.
    steer_cmd = int(CC.actuators.steer * 127)
    can_sends.append(self.packer.make_can_msg("STEERING_COMMAND", 0, {"STEER_VALUE": steer_cmd}))

    # 3. Create the ACTUATOR_COMMAND for throttle and brake.
    # CC.actuators.accel is a float. Positive means accelerate, negative means brake.
    throttle_cmd = 0
    brake_cmd = 0

    if CC.enabled and CC.actuators.accel > 0:
      # If accelerating, map the 0.0-1.0 value to our 0-255 throttle range.
      throttle_cmd = int(CC.actuators.accel * 255)
    elif CC.enabled and CC.actuators.accel < 0:
      # If braking, map the 0.0-(-1.0) value to our 0-255 brake range.
      # We use -accel to make the value positive.
      brake_cmd = int(-CC.actuators.accel * 255)

    # The packer will place throttle_cmd in byte 0 and brake_cmd in byte 1,
    # exactly as defined in the DBC and expected by the Arduino.
    can_sends.append(self.packer.make_can_msg("ACTUATOR_COMMAND", 0, {
      "THROTTLE_VALUE": throttle_cmd,
      "BRAKE_VALUE": brake_cmd,
    }))

    # The function must return a dictionary containing the list of CAN messages.
    new_actuators = car.CarControl.Actuators.new_message()
    new_actuators.steer = CC.actuators.steer
    new_actuators.accel = CC.actuators.accel

    return new_actuators, can_sends
