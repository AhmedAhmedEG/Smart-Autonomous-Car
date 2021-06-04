from mpu6050 import mpu6050
import time
import math

mpu = mpu6050(0x68)

def fDist(a,b):
    return math.sqrt((a*a)+(b*b));


def fGet_y_rotation(x,y,z):
    radians = math.atan2(y, fDist(x,z))
    return math.degrees(radians);

def fGet_x_rotation(x,y,z):
    radians = math.atan2(x, fDist(y,z))
    return -math.degrees(radians);

def fGet_z_rotation(x,y,z):
    radians = math.atan2(z, fDist(x,y))
    return math.degrees(radians);

while True:
    print("Temp: " + str(mpu.get_temp()) + "\n")

    accel_data = mpu.get_acc_data()
    gyro_data = mpu.get_gyro_data()
    
    print("X Rotation: " + str(fGet_x_rotation(accel_data['x'], accel_data['y'], accel_data['z'])))
    print("Y Rotation: " + str(fGet_y_rotation(accel_data['x'], accel_data['y'], accel_data['z'])))
    print("Z Rotation: " + str(fGet_z_rotation(accel_data['x'], accel_data['y'], accel_data['z'])))
    
    print("-------------------------------")

    time.sleep(1)

