#!/usr/bin/env python3
from cereal import car
from selfdrive.car.scooter.values import CAR
from selfdrive.car import CarCustomizable

class CarInterface(CarCustomizable):
  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "scooter"
    ret.mass = 250  # kg
    ret.wheelbase = 1.2  # meters
    ret.centerToFront = ret.wheelbase * 0.4
    ret.steerRatio = 15.0
    ret.steerActuatorDelay = 0.1
    ret.steerLimitTimer = 1.0
    ret.openpilotLongitudinalControl = True

    # This is a custom port, so we force the car fingerprint
    ret.carFingerprint = CAR.SCOOTER

    return ret

  def _update(self, c):
    # This is where you would normally read status messages from the car.
    # Since our scooter doesn't send any, we just create a new CarState message.
    # The important vEgo value will be filled in by controlsd from GPS data.
    ret = self.CS.update(self.cp, self.cp_cam)
    return ret

  def _apply(self, c, now_nanos):
    # This calls the CarController's update method, which creates the CAN messages
    return self.CC.update(c, self.CS, now_nanos)
