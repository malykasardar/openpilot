from cereal.car import CarFingerprint

class CAR:
  SCOOTER = CarFingerprint.new_message(brand="infento", model="scooter")

DBC = {
  CAR.SCOOTER: "scooter_proper",
}
