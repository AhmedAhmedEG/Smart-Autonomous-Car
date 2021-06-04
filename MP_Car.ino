#include <Servo.h>
#include <NewPing.h>

const int MAF = 12; // Motor A Forward
const int MAB = 13; // Motor A Backward
const int MAE = 6; // Motor A Enable

const int MBF = 7; // Motor B Forward
const int MBB = 8; // Motor B Backward
const int MBE = 5; // Motor B Enable

const int BP = A2; // Buzzer Positive
const int BN = A5; // Buzzer Negative

const int led = 3;

const int speed = 150; // Motors speed

const int trigger = 4; // Ultrasonic Sensor's Trigger Pin
const int echo = 2; // Ultrasonic Sensor's Echo Pin
const int max_distance = 200; // Ultrasonic Sensor's Max Distance

int current_distance;
int left_distance;
int right_distance;
int mode=2;

bool isforward = false;

NewPing sonar(trigger, echo, max_distance);
Servo servo;

void setup() {
    Serial.begin(9600);

    pinMode(MAF, OUTPUT);
    pinMode(MAB, OUTPUT);
    pinMode(MAE, OUTPUT);
    
    pinMode(MBF, OUTPUT);
    pinMode(MBB, OUTPUT);
    pinMode(MBE, OUTPUT);
    
    pinMode(BP, OUTPUT);
    pinMode(BN, OUTPUT);
    
    pinMode(led, OUTPUT);
    
    servo.attach(9);
    servo.write(100);

    current_distance = sonar.convert_cm(sonar.ping_median());
}

void loop() {

  char data = readSerialPort();
  setMode(data);
  
  if (mode == 1) {

    if (data == 'f') {
      
      if (!isforward) {
        moveForward();
      }
      
    }
    
    else if (data == 'b') {
      moveBackward(); 
    }
    
    else if (data == 's') {
      moveStop();
    }

    else if (data == 'l') {
      turnLeft(0);
    }

    else if (data == 'r') {
      turnRight(0);
    }

  }
  
  else if (mode == 2) {

    if (data == 'f') {
      Serial.println("RC up received!");
      
      if (!isforward) {
        moveForward();
      }
      
    }
    
    else if (data == 's') {
      Serial.println("RC stop received!");
      moveStop();
    }
    
    else if (data == 'b') {
      Serial.println("RC back received");
      moveBackward();
    }
    
    else if (data == 'l') {
      Serial.println("RC left received!");
      turnLeft(0);
    }

    else if (data == 'r') {
      Serial.println("RC right received!");
      turnRight(0);
    }
    
  }
  
  else if (mode == 3) {
    
    current_distance = sonar.convert_cm(sonar.ping_median());
    delay(100);

    if (current_distance == 0 || current_distance > 50) {

      if (!isforward) {
        moveForward();
      }

    }

    else {
      
      moveStop();
      lookAround();
      decideDirection();

    }

  }

}

void moveForward() {
  
  Serial.println("I will move forward.");
  
  digitalWrite(MAF, HIGH);
  digitalWrite(MAB, LOW);
  
  digitalWrite(MBF, HIGH);
  digitalWrite(MBB, LOW);
  
  accelerate();
  
  isforward = true;
  
}

void moveBackward() {
  
  Serial.println("I will move backward.");
  
  digitalWrite(MAF, LOW);
  digitalWrite(MAB, HIGH);
  
  digitalWrite(MBF, LOW);
  digitalWrite(MBB, HIGH);

  accelerate();

  isforward = false;
  
}

void turnLeft(int d) {
   
  Serial.println("rga");
  Serial.println("I will turn left.");
  
  digitalWrite(MAF, HIGH);
  digitalWrite(MAB, LOW);
  
  digitalWrite(MBF, LOW);
  digitalWrite(MBB, HIGH);
  
  accelerate();
  
  if (d != 0) {
    delay(d);
    moveStop();
  }

}

void turnRight(int d) {
  
  Serial.println("rga");
  Serial.println("I will turn right.");
  
  digitalWrite(MAF, LOW);
  digitalWrite(MAB, HIGH);
  
  digitalWrite(MBF, HIGH);
  digitalWrite(MBB, LOW);
  
  accelerate();
  
  if (d != 0) {
    delay(d);
    moveStop();
  }
  
}

void turnAround() {
  
  Serial.println("rga");
  
  digitalWrite(MAF, HIGH);
  digitalWrite(MAB, LOW);;
  
  digitalWrite(MBF, LOW);
  digitalWrite(MBB, HIGH);
  
  accelerate();

  delay(1400);
  
  moveStop();

}

void moveStop() {

  digitalWrite(MAF, LOW);
  digitalWrite(MAB, LOW);
  
  digitalWrite(MBF, LOW);
  digitalWrite(MBB, LOW);

  analogWrite(MAE, 0);
  analogWrite(MBE, 0);

  isforward = false;

}

void lookAround() {
  
  moveStop();

  servo.write(30);
  delay(500);
  
  right_distance = sonar.convert_cm(sonar.ping_median());
  Serial.print("Right distnace is: ");
  Serial.println(right_distance);
  delay(100); // Minimum cooldown for the ultra sonic sensor

  servo.write(160);
  delay(600);

  left_distance = sonar.convert_cm(sonar.ping_median());
  Serial.print("Left distnace is: ");
  Serial.println(left_distance);
  delay(100); // Minimum cooldown for the ultra sonic sensor
  
  servo.write(100);
  delay(500);
  
}

void decideDirection() {
  
  if (left_distance == 0 || ((left_distance > right_distance) && left_distance > 20)) {
    Serial.println("I will go to left!");
    turnLeft(700);
  }

  else if (right_distance == 0  || ((right_distance > left_distance) &&  right_distance > 20)) {
    Serial.println("I will go to right!");
    turnRight(700);
  }

  else {
    turnAround();
    Serial.println("I will go away!");
  }
  
}

void accelerate() {
 
//  for (int s=0; s < speed; s += 2) {
//    analogWrite(MAE, s);
//    analogWrite(MBE, s);
//    delay(5);
//  }
  analogWrite(MAE, speed);
  analogWrite(MBE, speed);
}

void buzz(int d, int c) {
  
  int i = 0;
  while (i != c) {

    digitalWrite(BP, HIGH);
    digitalWrite(BN, LOW);

    delay(d);

    digitalWrite(BP, LOW);
    digitalWrite(BN, LOW);

    delay(d);
    i += 1;

  }
   
}

char readSerialPort() {

  if (Serial.available()) {
    char msg = (char)Serial.read();
    while (Serial.read() >= 0){continue;}
    return msg;
  }

}

void setMode(char data) {

  if (data == '1') {
    
    buzz(62, 3);
    if (mode != 1) {
      mode = 1;
      moveStop();
      
      servo.write(100);
      delay(500);
      
      Serial.println("Mode 1 set.");
      digitalWrite(led, HIGH);
    }
    
  }

  else if (data == '2') {
    
    buzz(62, 3);
    if (mode != 2) {
      mode = 2;
      moveStop();
      
      servo.write(100);
      delay(500);
      
      Serial.println("Mode 2 set.");
      digitalWrite(led, LOW);
    }
    
  }

  else if (data == '3') {
    
    buzz(62, 3);
    if (mode != 3) {
      mode = 3;
      moveStop();
      
      servo.write(100);
      delay(500);
      
      Serial.println("Mode 3 set.");
      digitalWrite(led, LOW);
    }
    
  }

}
