"""This program handles the communication over I2C
between a Raspberry Pi and a MPU-6050 Gyroscope / Accelerometer combo.
Made by: MrTijn/Tijndagamer
Released under the MIT License
Copyright (c) 2015, 2016, 2017 MrTijn/Tijndagamer
"""
import cmath
import math
import time
import smbus


class Mpu6050:

    # Global Variables
    GRAVITY_MS2 = 9.80665
    address = None
    bus = None

    # Scale Modifiers
    ACC_SCALE_MODIFIER_2G = 16384.0
    ACC_SCALE_MODIFIER_4G = 8192.0
    ACC_SCALE_MODIFIER_8G = 4096.0
    ACC_SCALE_MODIFIER_16G = 2048.0

    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Pre-defined ranges
    ACC_RANGE_2G = 0x00
    ACC_RANGE_4G = 0x08
    ACC_RANGE_8G = 0x10
    ACC_RANGE_16G = 0x18

    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACC_XOUT0 = 0x3B
    ACC_YOUT0 = 0x3D
    ACC_ZOUT0 = 0x3F

    TEMP_OUT0 = 0x41

    GYRO_XOUT0 = 0x43
    GYRO_YOUT0 = 0x45
    GYRO_ZOUT0 = 0x47

    ACC_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    def __init__(self, address, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)
        # Wake up the MPU-6050 since it starts in sleep mode
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
        self.current_time = time.time()

        #Rotation angles from accelerator data.
        #We can't calculate rotation angle in Z axis from accelerator, because gravity always points to one direction.
        self.acc_angle_x = 0
        self.acc_angle_y = 0

        #Rotations angles from gyroscope data.
        self.gyro_angle_x = 0
        self.gyro_angle_y = 0
        self.gyro_angle_z = 0

        #Finale true rotation angles, will be calculated by combining gyroscope and accelerator data.
        #Yaw will be the gyroscope reading only, because the accelerator can't get rotation values on z axis as explained before.
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

    # I2C communication methods

    def read_i2c_word(self, register):
        """Read two i2c registers and combine them.

        register -- the first register to read from.
        Returns the combined read results.
        """
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if value >= 0x8000:
            return -((65535 - value) + 1)
        else:
            return value

    # MPU-6050 Methods

    def get_temp(self):
        """Reads the temperature from the onboard temperature sensor of the MPU-6050.

        Returns the temperature in degrees Celcius.
        """
        raw_temp = self.read_i2c_word(self.TEMP_OUT0)

        # Get the actual temperature using the formula given in the
        # MPU-6050 Register Map and Descriptions revision 4.2, page 30
        actual_temp = (raw_temp / 340.0) + 36.53

        return actual_temp

    def set_acc_range(self, accel_range):
        """Sets the range of the accelerometer to range.

        accel_range -- the range to set the accelerometer to. Using a
        pre-defined range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.ACC_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACC_CONFIG, accel_range)

    def read_acc_range(self, raw=False):
        """Reads the range the accelerometer is set to.

        If raw is True, it will return the raw value from the ACCEL_CONFIG
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.ACC_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACC_RANGE_2G:
                return 2
            elif raw_data == self.ACC_RANGE_4G:
                return 4
            elif raw_data == self.ACC_RANGE_8G:
                return 8
            elif raw_data == self.ACC_RANGE_16G:
                return 16
            else:
                return -1

    def get_acc_data(self, g=False):
        """Gets and returns the X, Y and Z values from the accelerometer.

        If g is True, it will return the data in g
        If g is False, it will return the data in m/s^2
        Returns a dictionary with the measurement results.
        """
        acc_x = self.read_i2c_word(self.ACC_XOUT0)
        acc_y = self.read_i2c_word(self.ACC_YOUT0)
        acc_z = self.read_i2c_word(self.ACC_ZOUT0)

        acc_scale_modifier = None
        accel_range = self.read_acc_range(True)

        if accel_range == self.ACC_RANGE_2G:
            acc_scale_modifier = self.ACC_SCALE_MODIFIER_2G
        elif accel_range == self.ACC_RANGE_4G:
            acc_scale_modifier = self.ACC_SCALE_MODIFIER_4G
        elif accel_range == self.ACC_RANGE_8G:
            acc_scale_modifier = self.ACC_SCALE_MODIFIER_8G
        elif accel_range == self.ACC_RANGE_16G:
            acc_scale_modifier = self.ACC_SCALE_MODIFIER_16G
        else:
            print("Unknown range - acc_scale_modifier set to self.ACC_SCALE_MODIFIER_2G")
            acc_scale_modifier = self.ACC_SCALE_MODIFIER_2G

        acc_x = acc_x / acc_scale_modifier
        acc_y = acc_y / acc_scale_modifier
        acc_z = acc_z / acc_scale_modifier

        #0.58 and 1.58 are used for error reduction
        try:
            self.acc_angle_x = (math.atan(acc_y / (math.sqrt(acc_x**2 + acc_z**2))) * (180 / math.pi)) - 0.58

        except ZeroDivisionError:
            self.acc_angle_x = 0

        try:
            self.acc_angle_y = (math.atan(-1 * acc_x / math.sqrt(acc_y**2 + acc_y**2)) * (180 / math.pi)) + 1.58

        except ZeroDivisionError:
            self.acc_angle_y = 0

        if not g:
            acc_x = acc_x * self.GRAVITY_MS2
            acc_y = acc_y * self.GRAVITY_MS2
            acc_z = acc_z * self.GRAVITY_MS2

        return {'raw': [acc_x, acc_y, acc_z], 'angle': [self.acc_angle_x, self.acc_angle_y]}

    def set_gyro_range(self, gyro_range):
        """Sets the range of the gyroscope to range.

        gyro_range -- the range to set the gyroscope to. Using a pre-defined
        range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyro_range)

    def read_gyro_range(self, raw=False):
        """Reads the range the gyroscope is set to.

        If raw is True, it will return the raw value from the GYRO_CONFIG
        register.
        If raw is False, it will return 250, 500, 1000, 2000 or -1. If the
        returned value is equal to -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.GYRO_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == self.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == self.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    def get_gyro_data(self):
        """Gets and returns the X, Y and Z values from the gyroscope.

        Returns the read values in a dictionary.
        """
        previous_time = self.current_time
        self.current_time = time.time()
        elapsed_time = self.current_time - previous_time

        gyro_x = self.read_i2c_word(self.GYRO_XOUT0)
        gyro_y = self.read_i2c_word(self.GYRO_YOUT0)
        gyro_z = self.read_i2c_word(self.GYRO_ZOUT0)

        gyro_scale_modifier = None
        gyro_range = self.read_gyro_range(True)

        if gyro_range == self.GYRO_RANGE_250DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG
        elif gyro_range == self.GYRO_RANGE_500DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_500DEG
        elif gyro_range == self.GYRO_RANGE_1000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_1000DEG
        elif gyro_range == self.GYRO_RANGE_2000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_2000DEG
        else:
            print("Unknown range - gyro_scale_modifier set to self.GYRO_SCALE_MODIFIER_250DEG")
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG

        gyro_x = gyro_x / gyro_scale_modifier
        gyro_y = gyro_y / gyro_scale_modifier
        gyro_z = gyro_z / gyro_scale_modifier

        #Error correction
        gyro_x += 0.56
        gyro_y += -2
        gyro_z += 0.79

        #Converting gyroscope data from degrees/s to degrees only.
        self.gyro_angle_x += gyro_x * elapsed_time
        self.gyro_angle_y += gyro_y * elapsed_time
        self.gyro_angle_z += gyro_z * elapsed_time

        return {'raw': [gyro_x, gyro_y, gyro_z], 'angle': [self.gyro_angle_x, self.gyro_angle_y, self.gyro_angle_z]}

    def reset_gyro_angles(self):
        self.gyro_angle_x = 0
        self.gyro_angle_y = 0
        self.gyro_angle_z = 0

    def get_rotations(self):

        gyro = self.get_gyro_data()

        self.roll = 0.96 * self.gyro_angle_x + 0.04 * self.acc_angle_x
        self.pitch = 0.96 * self.gyro_angle_y + 0.04 * self.acc_angle_y
        self.yaw = self.gyro_angle_z

        return [gyro, [self.roll, self.pitch, self.yaw]]

    def get_all_data(self):
        """Reads and returns all the available data."""
        temp = self.get_temp()
        acc = self.get_acc_data()
        gyro, rotations = self.get_rotations()

        return [temp, acc, gyro, rotations]


if __name__ == "__main__":
    mpu = Mpu6050(0x68)

    while True:
        data = mpu.get_all_data()

        temp = data[0]
        print("-------------------------------")
        print("Temperature: ", temp, "\n")

        acc_data = data[1]
        print(f"Accelerator Raw: ({acc_data['raw'][0]}, {acc_data['raw'][1]}, {acc_data['raw'][2]})\n")
        print(f"Accelerator Rotation: ({acc_data['angle'][0]}, {acc_data['angle'][1]})\n", )

        gyro_data = data[2]
        print(f"Gyro Raw: ({gyro_data['raw'][0]}, {gyro_data['raw'][1]}, {gyro_data['raw'][2]})\n")
        print(f"Gyro Rotation: ({gyro_data['angle'][0]}, {gyro_data['angle'][1]}, {gyro_data['angle'][2]})\n")

        rotations_data = data[3]
        print("Roll: ", rotations_data[0])
        print("Pitch: ", rotations_data[1])
        print("Yaw: ", rotations_data[2])
        print("-------------------------------")
        time.sleep(0.5)
