#include <ESP32Servo.h>

Servo panServo;  
Servo tiltServo; 

const int panPin = 18;  
const int tiltPin = 19; 

// Hız ayarı: İki derece arasındaki bekleme süresi (Milisaniye)
// Bu sayı büyüdükçe servo daha YAVAŞ döner.
const int servoHizGecikmesi = 30; 

void setup() {
  Serial.begin(115200);
  delay(1000); 
  
  Serial.println("=== YAVAS PAN-TILT MODU BASLADI ===");

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  
  panServo.setPeriodHertz(50);    
  tiltServo.setPeriodHertz(50);

  panServo.attach(panPin, 500, 2400); 
  tiltServo.attach(tiltPin, 500, 2400);
  
  // Başlangıçta servoları tam orta noktaya (90 dereceye) getiriyoruz
  Serial.println("[SISTEM] Servolar merkezleniyor (90 derece)...");
  panServo.write(90);
  tiltServo.write(90);
  delay(1000); // Merkeze ulaşmaları için güvenli bir bekleme
}

void loop() {
  // ===================================================
  // --- 1. ADIM: YATAY (PAN) HAREKETİ (45° ile 135° Arası = 90 Derecelik Alan) ---
  // ===================================================
  
  // Merkezden (90) sağa doğru (135) yavaşça dönüyoruz
  Serial.println("[LOG] Pan Servosu: 90 -> 135 dereceye yavasca donuyor...");
  for (int aci = 90; aci <= 135; aci += 1) {
    panServo.write(aci);
    delay(servoHizGecikmesi); 
  }
  delay(800); 
  
  // En sağdan (135) en sola (45) yavaşça dönüyoruz
  Serial.println("[LOG] Pan Servosu: 135 -> 45 dereceye yavasca donuyor...");
  for (int aci = 135; aci >= 45; aci -= 1) {
    panServo.write(aci);
    delay(servoHizGecikmesi);
  }
  delay(800); 

  // En soldan (45) tekrar merkez noktasına (90) geri geliyoruz
  Serial.println("[LOG] Pan Servosu: 45 -> 90 dereceye (Merkeze) donuyor...");
  for (int aci = 45; aci <= 90; aci += 1) {
    panServo.write(aci);
    delay(servoHizGecikmesi);
  }
  delay(1000); // Dikey harekete geçmeden önce kısa bir mola


  // ===================================================
  // --- 2. ADIM: DİKEY (TILT) HAREKETİ (45° ile 135° Arası = 90 Derecelik Alan) ---
  // ===================================================
  
  // Merkezden (90) yukarıya (135) yavaşça kalkıyor
  Serial.println("[LOG] Tilt Servosu: 90 -> 135 dereceye yavasca kalkiyor...");
  for (int aci = 90; aci <= 135; aci += 1) { 
    tiltServo.write(aci);
    delay(servoHizGecikmesi);
  }
  delay(800); 
  
  // En yukarıdan (135) en aşağıya (45) yavaşça iniyor
  Serial.println("[LOG] Tilt Servosu: 135 -> 45 dereceye yavasca iniyor...");
  for (int aci = 135; aci >= 45; aci -= 1) {
    tiltServo.write(aci);
    delay(servoHizGecikmesi);
  }
  delay(800); 
  
  // En aşağıdan (45) tekrar merkez noktasına (90) geri geliyor
  Serial.println("[LOG] Tilt Servosu: 45 -> 90 dereceye (Merkeze) donuyor...");
  for (int aci = 45; aci <= 90; aci += 1) {
    tiltServo.write(aci);
    delay(servoHizGecikmesi);
  }
  
  Serial.println("-----------------------------------------------------");
  delay(2000); // Yeni döngü başlamadan önce merkezde 2 saniye bekle
}