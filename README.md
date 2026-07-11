# ESP32 Çalışmaları

ESP32 ve Raspberry Pi tabanlı, kamera/sensör verisiyle donanımı gerçek zamanlı kontrol eden küçük gömülü sistem projelerinin bir araya toplandığı repo.

## İçindekiler

| Klasör | Açıklama |
|---|---|
| [`button_mpu6050/`](button_mpu6050) | MPU6050 ivme/jiroskop sensöründen roll açısı hesaplayan ve buton girişini okuyan ESP32 (Arduino) firmware'i. |
| [`hand_servo/`](hand_servo) | MediaPipe ile el takibi yaparak tespit edilen el konumuna göre ESP32 üzerindeki pan/tilt servolarını seri port üzerinden kontrol eden proje. Detaylı kurulum ve çalıştırma adımları için [alt klasördeki README](hand_servo/README.md)'ye bakın. |
| [`pan-tilt_pi/`](pan-tilt_pi) | Raspberry Pi üzerinde `rpicam-vid` ile alınan kamera görüntüsünden el takibi (`el.py`) yapıp, sonucu seri port üzerinden ESP32'ye gönderen pan-tilt kontrol betikleri. |

## Donanım

- ESP32 geliştirme kartı
- MPU6050 ivme/jiroskop sensörü
- 360° sürekli dönüş servo motorlar (pan/tilt)
- Raspberry Pi + kamera modülü (pan-tilt_pi için)

## Kurulum

```bash
pip install opencv-python mediapipe pyserial numpy
```

ESP32 tarafı için Arduino IDE ile ilgili `.ino` dosyasını karta yükleyin. Python betiklerindeki seri port adını (`COM4`, `/dev/ttyUSB0` vb.) kendi ortamınıza göre güncelleyin.
