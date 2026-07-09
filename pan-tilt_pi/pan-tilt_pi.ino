#include <ESP32Servo.h>

// Servo nesnelerini tanımlıyoruz
Servo panServo;
Servo tiltServo;

// Motor pin tanımlamaları (Belirttiğin gibi alt 18, üst 19)
const int panPin = 18;  // Alt motor (Yatay)
const int tiltPin = 19; // Üst motor (Dikey)

void setup() {
  // Raspberry Pi ile iletişim kurmak için seri portu başlatıyoruz
  Serial.begin(115200);
  
  // Servoları ilgili pinlere bağlıyoruz
  panServo.attach(panPin);
  tiltServo.attach(tiltPin);
  
  // Başlangıçta motorları durduruyoruz (Nötr noktası: 96)
  panServo.write(96);
  tiltServo.write(96);
  
  Serial.println("ESP32 Hazir. Komut bekleniyor...");
}

void loop() {
  // Seri porttan veri gelip gelmediğini kontrol ediyoruz
  if (Serial.available() > 0) {
    // Gelen veriyi satır sonuna (\n) kadar oku
    String veri = Serial.readStringUntil('\n');
    veri.trim(); // Varsa boşlukları temizle
    
    // Veri paketini virgül karakterine göre ayırıyoruz (Örn: "105,87")
    int virgulIndeks = veri.indexOf(',');
    
    if (virgulIndeks != -1) {
      // Virgülün solundaki ve sağındaki değerleri ayıkla
      String panStr = veri.substring(0, virgulIndeks);
      String tiltStr = veri.substring(virgulIndeks + 1);
      
      // Metinleri tam sayıya (int) çevir
      int panKomut = panStr.toInt();
      int tiltKomut = tiltStr.toInt();
      
      // Geçerli değer aralığı kontrolü (Güvenlik için 0-180 arası)
      if (panKomut >= 0 && panKomut <= 180 && tiltKomut >= 0 && tiltKomut <= 180) {
        // Değerleri servolara uygula (360 derece servo için yön ve hız belirtir)
        panServo.write(panKomut);
        tiltServo.write(tiltKomut);
      }
    }
  }
}