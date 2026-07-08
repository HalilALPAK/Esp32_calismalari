#include <Wire.h>

const int MPU_addr = 0x68; 
int16_t AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ;
const int butonPin = 5;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  pinMode(butonPin, INPUT);
  
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission();
}

void loop() {
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B); 
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr, 14, true); 

  AcX = Wire.read() << 8 | Wire.read();  
  AcY = Wire.read() << 8 | Wire.read();  
  AcZ = Wire.read() << 8 | Wire.read();  
  Tmp = Wire.read() << 8 | Wire.read();  
  GyX = Wire.read() << 8 | Wire.read();  
  GyY = Wire.read() << 8 | Wire.read();  
  GyZ = Wire.read() << 8 | Wire.read();  

  float roll = atan2(AcY, AcZ) * 180.0 / PI;
  float pitch = atan2(-AcX, sqrt((long)AcY * AcY + (long)AcZ * AcZ)) * 180.0 / PI;

  // Buton durumunu oku (Basıldıysa 1, basılmadıysa 0 gönderelim Python rahat anlasın)
  int butonDurumu = (digitalRead(butonPin) == LOW) ? 1 : 0;

  // Python'ın okuyacağı format: Roll,Pitch,Buton
  Serial.print(roll);
  Serial.print(",");
  Serial.print(pitch);
  Serial.print(",");
  Serial.println(butonDurumu);

  delay(20); 
}