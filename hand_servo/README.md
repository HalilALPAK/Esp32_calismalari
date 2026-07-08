# Hand Servo — El Hareketiyle 360° Servo Kontrolü

Bilgisayar kamerasından MediaPipe ile el takibi yapılarak, tespit edilen el konumuna göre ESP32 üzerindeki iki adet 360° sürekli dönüş servosunun (pan/tilt) seri port üzerinden kontrol edildiği bir proje.

## Nasıl Çalışır

1. `EL_SERVO/EL_SERVO.PY` bilgisayarın kamerasını açar, MediaPipe Hands ile eldeki `Right`/`Left` etiketlerini ve bilek (landmark 0) konumunu tespit eder.
2. **Sağ el** ekranın yatayında (X ekseni) merkezden sola/sağa kayınca **pan** motorunun yönünü belirler.
3. **Sol el** ekranın dikeyinde (Y ekseni) merkezden yukarı/aşağı kayınca **tilt** motorunun yönünü belirler.
4. Merkeze yakın bölgede (`deadzone = 0.1`) motorlar durma komutu alır.
5. Hesaplanan `pan_komut,tilt_komut\n` formatındaki metin, seri port (varsayılan `COM4`, 115200 baud) üzerinden ESP32'ye gönderilir.
6. `hand_servo.ino` bu veriyi okuyup virgülden ayırır ve değerleri doğrudan `panServo.write()` / `tiltServo.write()` ile servolara uygular.

## Komut Değerleri

Kod, sürekli dönüş (continuous rotation) servoları için kalibre edilmiştir; `write()` değeri açı değil **dönüş hızı/yönünü** belirtir:

| Değer | Anlamı |
|-------|--------|
| `96`  | Dur (nötr nokta) |
| `105` | Yavaşça bir yöne dön (sağa / yukarı) |
| `87`  | Yavaşça diğer yöne dön (sola / aşağı) |

> Kullandığınız servo modeline göre nötr nokta (`96`) farklılık gösterebilir; ilk kurulumda bu değeri kendi servonuza göre kalibre etmeniz gerekebilir.

## Donanım

- ESP32 geliştirme kartı
- 2× 360° sürekli dönüş servo motor
  - Pan servo → GPIO **18**
  - Tilt servo → GPIO **19**
- USB kamera (bilgisayar üzerinde)

## Kurulum

### ESP32 (Arduino)

1. Arduino IDE'de `ESP32Servo` kütüphanesini kurun.
2. `hand_servo.ino` dosyasını ESP32 kartına yükleyin.
3. Servoları belirtilen GPIO pinlerine bağlayın.

### Python tarafı

`EL_SERVO/` klasöründe bir `venv` sanal ortamı mevcuttur. Gerekli paketler:

```bash
pip install opencv-python mediapipe pyserial
```

`EL_SERVO.PY` içindeki seri port adını (`COM4`) kendi ESP32'nizin bağlı olduğu porta göre güncelleyin.

## Çalıştırma

```bash
cd hand_servo/EL_SERVO
python EL_SERVO.PY
```

- Kamera görüntüsü açılır, tespit edilen el(ler) iskelet olarak çizilir, ekranda anlık pan/tilt komut değerleri gösterilir.
- Ekranda mavi çizgiler, X/Y merkez eksenlerini gösterir.
- Çıkmak için `q` tuşuna basın.

## Dosya Yapısı

```
hand_servo/
├── hand_servo.ino          # ESP32 firmware — seri porttan pan/tilt komutu okuyup servolara uygular
└── EL_SERVO/
    ├── EL_SERVO.PY          # MediaPipe ile el takibi yapıp ESP32'ye komut gönderen Python betiği
    └── venv/                # Python sanal ortamı
```
