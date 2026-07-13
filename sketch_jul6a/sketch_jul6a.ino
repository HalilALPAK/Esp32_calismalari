const int butonPin = 5; // S pini D5'te kalmaya devam etsin, gayet kararlı

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- Ters Mantigi Duzeltilmis Buton Testi ---");
  
  pinMode(butonPin, INPUT); 
}

void loop() {
  int ilkOkuma = digitalRead(butonPin);

  // Modül ters çalıştığı için: Basılmadığında HIGH, basıldığında LOW olur.
  // Eğer pin LOW (0) olduysa buton tetiklenmiş olabilir, kontrol edelim:
  if (ilkOkuma == LOW) {
    delay(30); // Filtre (Debounce) süresi
    int ikinciOkuma = digitalRead(butonPin);
    
    // 30 ms sonra hala LOW ise butona parmakla basılıyordur
    if (ikinciOkuma == LOW) {
      Serial.println("\nDURUM: [ BUTONA BASILDI ]");
      delay(200); // Ekranı kilitlememesi için kısa bir bekleme
    }
  } 
  else {
    // Butona basılmıyorsa ekranda sadece noktalar akacak
    Serial.print("."); 
    delay(50);
  }
}