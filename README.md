# Multipurpose-Vehicle
A multi-mode DIY car that can perform object tracking, collision detection and RC control

![191525680_308942670774706_8325018400669418868_n](https://user-images.githubusercontent.com/16827679/120732199-31fab180-c4e5-11eb-9cd0-dbf933b72d3b.jpg)
![192235505_637634110525807_6239004647480705682_n](https://user-images.githubusercontent.com/16827679/120732211-358e3880-c4e5-11eb-8138-e7f1f0278371.jpg)
![191979636_324835885947616_6728941936257660862_n](https://user-images.githubusercontent.com/16827679/120732217-3757fc00-c4e5-11eb-875a-9d4d578baa35.jpg)
![All-In-One Car_bb](https://user-images.githubusercontent.com/16827679/120732269-49399f00-c4e5-11eb-8ba4-a867c491f794.png)
https://www.youtube.com/watch?v=-7l7ddGZTMU&ab_channel=AhmedAhmedEG


# Contents
MP_Car.py: is the main controller, it handles modes functions, camera, gyroscope, bluetooth commands and controlling arduino.

MP_Car.ino: is the arduino code that handels the motor driver, ultrasonic sensor, servo motor and the buzzer.

Mask_Creator.py: a simple script with GUI trackers, it's purpose is to get values needed for filtering the wanted color for object detection.

Modules/mpu6050.py: is a modified version of m-rtijn's mpu6050 python library (https://github.com/m-rtijn) that's eaiser to use and includes calculations for rotations angles, logging for all usefull sensor information and with error reduction technique.

Modules/utils.py: includes funtions used in MP_Car.py for hardware detection, data gathering and error handling.

# Full Info Report

[Low Cost Autonomous Vehicle Based On Efficient Color Filtering Algorithm.docx](https://github.com/AhmedAhmedEG/Autonomous-Multiporpuse-Vehicle/files/8238477/Low.Cost.Autonomous.Vehicle.Based.On.Efficient.Color.Filtering.Algorithm.docx)

# Needed Libraries
python3 -m pip install opencv-python

python3 -m pip install pyserial

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
