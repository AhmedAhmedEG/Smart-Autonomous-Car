import cv2
import serial
import time


def check_arduino():
    arduino = None
    port = 0

    while True:

        try:
            arduino = serial.Serial("/dev/ttyACM" + str(port), 9600, timeout=1)
            print("Connected to the arduino board!")
            break

        except serial.serialutil.SerialException:
            print("Can't connect to the arduino board.")

            if port != 4:
                port += 1

            else:
                port = 0

            time.sleep(0.5)
            continue

    return arduino


def check_bluetooth():
    bluetooth = None

    while True:

        try:
            bluetooth = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
            print("Connected to the bluetooth chip!")
            break

        except serial.serialutil.SerialException:
            print("Can't connect to the bluetooth chip.")
            time.sleep(0.5)
            continue

    return bluetooth


def check_camera():

    camera = None
    mid_frame_x = None

    fails = 0
    while True:

        camera = cv2.VideoCapture(0)
        if camera is None or not camera.isOpened():
            print("Can't find a camera.\n")
            time.sleep(0.5)

            if fails != 5:
                fails += 1

            else:
                print("Camera check stopped.\n")
                camera = None
                break

        else:
            mid_frame_x = (camera.get(3)/2)
            break

    return camera, mid_frame_x


def get_data(bluetooth, arduino):
    bluetooth_data = None
    arduino_data = None

    if bluetooth.inWaiting() != 0:
        bluetooth_data = bluetooth.read(1)

    if arduino.inWaiting() != 0:
        arduino_data = ""

        while "\n" not in arduino_data:

            try:
                arduino_data += (arduino.read()).decode()

            except serial.serialutil.SerialException:
                arduino_data = ""

        if arduino_data != "":
            arduino_data.strip("\n")

        else:
            arduino_data = None

    return bluetooth_data, arduino_data


def get_hardware():
    return check_arduino(), check_bluetooth()
