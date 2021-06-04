# Multipurpose-Car
A multi-mode DIY car that can perform object tracking, collision detection and RC control

# Contents
MP_Car.py: is the main controller, it handles modes functions, camera, gyroscope, bluetooth commands and controlling arduino.

MP_Car.ino: is the arduino code that handels the motor driver, ultrasonic sensor, servo motor and the buzzer.

Mask_Creator.py: a simple script with GUI trackers, it's purpose is to get values needed for filtering the wanted color for object detection.

Modules/mpu6050.py: is a modified version of m-rtijn's mpu6050 python library (https://github.com/m-rtijn) that's eaiser to use and includes calculations for rotations angles with error reduction.

Modules/utils.py: includes funtions used in MP_Car.py for hardware detection, data gathering and error handling.

# Needed Libraries
python3 -m pip install opencv-python

pythom3 -m pip install imutils

pythom3 -m pip install numpy

sudo apt install python3-smbus

# Opencv erros in rasbian OS
Firstly, update everthing:-

sudo apt-get update && sudo apt-get upgrade && sudo rpi-update

sude reboot

Then install tools needed for opencv:-

sudo apt-get install libcblas-dev

sudo apt-get install libhdf5-dev

sudo apt-get install libhdf5-serial-dev

sudo apt-get install libatlas-base-dev

sudo apt-get install libjasper-dev 

sudo apt-get install libqtgui4 

sudo apt-get install libqt4-test

# If blutooth does not exist even when connected correctly
Follow this instructions:-
![Screenshot_1](https://user-images.githubusercontent.com/16827679/120731712-720d6480-c4e4-11eb-8628-7e06d255aa3c.png)
