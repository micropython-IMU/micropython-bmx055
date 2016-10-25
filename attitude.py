import math

def angle(imu_data):
    x,y,z = imu_data
    roll = math.atan(x/math.sqrt(y**2+z**2))
    pitch = math.atan(y/math.sqrt(x**2+z**2))
    return (roll, pitch)
