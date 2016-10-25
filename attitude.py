import math

def angles(imu_data: tuple) -> tuple:
    '''
    Returns a list containing roll and pitch in degrees, calculated from 
    acceleration of x,y and z axis in g.
    '''
    x,y,z = imu_data
    pitch = math.atan(x/math.sqrt(y**2+z**2))
    roll = math.atan(y/math.sqrt(x**2+z**2))
    return (math.degrees(roll), math.degrees(pitch))
