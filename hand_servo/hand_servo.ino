#include <ESP32Servo.h>

Servo panServo;  
Servo tiltServo; 

const int panPin = 18;  
const int tiltPin = 19; 

void setup() {
  Serial.begin(115200); 
  delay(1000); 
  
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  
  panServo.setPeriodHertz(50);    
  tiltServo.setPeriodHertz(50);

  panServo.attach(panPin, 500, 2400); 
  tiltServo.attach(tiltPin, 500, 2400);
  
  // Kalibrasyon sonucuna göre yeni durma noktamız: 96
  panServo.write(96);
  tiltServo.write(96);
  Serial.println("SISTEM HAZIR: 360 Derece Kalibre Edilmis Mod.");
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    data.trim(); 
    
    int commaIndex = data.indexOf(',');
    if (commaIndex != -1) {
      String panStr = data.substring(0, commaIndex);
      String tiltStr = data.substring(commaIndex + 1);
      
      int panHizYon = panStr.toInt();
      int tiltHizYon = tiltStr.toInt();
      
      // Gelen komutları doğrudan motorlara yaz
      panServo.write(panHizYon);
      tiltServo.write(tiltHizYon);
    }
  }
}