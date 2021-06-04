import cv2
import imutils
import numpy as np
import time
from Modules.utils import get_hardware, get_data, check_camera
from Modules.mpu6050 import Mpu6050

mpu = Mpu6050(0x68)

color_dict_HSV = {'black': [[180, 255, 30], [0, 0, 0]],
                  'white': [[180, 18, 255], [0, 0, 231]],
                  'red1': [[180, 255, 255], [159, 50, 70]],
                  'red2': [[5, 255, 255], [0, 110, 110]],
                  'green': [[89, 255, 255], [36, 50, 70]],
                  'blue': [[128, 255, 255], [90, 50, 70]],
                  'yellow': [[35, 255, 255], [25, 50, 70]],
                  'purple': [[158, 255, 255], [129, 50, 70]],
                  'orange': [[24, 255, 255], [10, 50, 70]],
                  'gray': [[180, 18, 230], [0, 0, 40]]}

lower_color = np.array(color_dict_HSV["red2"][1])
upper_color = np.array(color_dict_HSV["red2"][0])

arduino, bluetooth = get_hardware()

mode = 0
direction = ""
mid_frame_x = None
camera = None


def check_serials():
    global mode, camera,  mid_frame_x

    bluetooth_data, arduino_data = get_data(bluetooth, arduino)

    if bluetooth_data is not None:

        if bluetooth_data == b"1":

            camera, mid_frame_x = check_camera()

            if camera is not None:
                mode = 1
                arduino.write(bluetooth_data)

            else:
                mode = 0

        elif bluetooth_data == b"2":
            
            if mode == 1:
                camera.release()
                cv2.destroyAllWindows()
            
            mode = 2
            arduino.write(bluetooth_data)

        elif bluetooth_data == b"3":
            
            if mode == 1:
                camera.release()
                cv2.destroyAllWindows()
            
            mode = 3 
            arduino.write(bluetooth_data)

    if arduino_data is not None:
        print(arduino_data)

        if arduino_data == "rg":
            mpu.reset_gyro_angles()

    return bluetooth_data, arduino_data


while True:
    bluetooth_data, arduino_data = check_serials()
    
    if mode == 1:
        
        fails = 0
        while True:
            
            try:
                _, frame = camera.read()
                break

            except cv2.error:
                print("Can't find a camera.\n")
                time.sleep(0.5)

                if fails != 5:
                    fails += 1
                    continue

                else:
                    print("Camera check stopped.\n")
                    cv2.destroyAllWindows()
                    mode = False
                    break

        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_color, upper_color)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # Contours detection
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            if radius > 50:
                
                if direction in ["f", "b"]:
                    
                    if 100 < radius < 180:
                        print("s")
                        arduino.write("s".encode())
                        direction = ""

                elif radius > 180:
                    print("b")
                    arduino.write("b".encode())
                    direction = "b"

                elif radius < 100:
                    print("f")
                    arduino.write("f".encode())
                    direction = "f"
                
                if direction in ["r", "l"]:

                    if mid_frame_x + 160 > x > mid_frame_x - 160:
                        print("s")
                        arduino.write("s".encode())
                        direction = ""
                    
                elif x > mid_frame_x + 120:
                    print("r")
                    arduino.write("r".encode())
                    direction = "r"

                elif x < mid_frame_x - 120:
                    print("l")
                    arduino.write("l".encode())
                    direction = "l"

                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.line(frame, (int(x), 0), (int(x), 480), (0, 255, 0), 3)
                cv2.line(frame, (0, int(y)), (640, int(y)), (0, 255, 0), 3)

            else:

                if direction == "f":
                    print("s")
                    arduino.write("s".encode())
                    direction = ""
        else:

            if direction == "f":
                print("s")
                arduino.write("s".encode())
                direction = ""

        cv2.imshow("Camera", frame)
        cv2.imshow("Mask", mask)
        key = cv2.waitKey(1)

    elif mode == 2 and bluetooth_data is not None:
        print(bluetooth_data)
        if bluetooth_data in [b"f", b"s"]:
            arduino.write(bluetooth_data)

        elif bluetooth_data == b"l":
            arduino.write(bluetooth_data)
            mpu.reset_gyro_angles()
            
            mpu.get_all_data()
            yaw = mpu.yaw

            while mpu.yaw > yaw - 85:
                mpu.get_all_data()
                pass

            arduino.write(b"s")

        elif bluetooth_data == b"r":
            arduino.write(bluetooth_data)
            mpu.reset_gyro_angles()
            
            mpu.get_all_data()
            yaw = mpu.yaw
            
            while mpu.yaw < yaw + 85:
                mpu.get_all_data()
                print(mpu.yaw)
                pass

            arduino.write(b"s")
