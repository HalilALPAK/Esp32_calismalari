# -*- coding: utf-8 -*-
import cv2
import numpy as np
import subprocess
import time
import serial
import mediapipe as mp

def main():
    # --- ESP32 Bağlantısı ---
    try:
        esp32 = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=0.1)
        print("ESP32 baglantisi basarili.")
        time.sleep(2)
    except Exception as e:
        print(f"ESP32 port hatasi! /dev/ttyACM0 yapmayi deneyin. Hata: {e}")
        return

    # --- MediaPipe Kurulumu ---
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.6)

    # --- Optimize rpicam-vid Komutu ---
    # Çözünürlüğü ve FPS'i Pi'yi yormayacak stabil değerlere çektik
    command = [
        'rpicam-vid', '--camera', '0', '--width', '480', '--height', '480',
        '--codec', 'mjpeg', '--inline', '--timeout', '0', '--nopreview', 
        '--flush', '--framerate', '30', '-o', '-'
    ]
    
    # Bufsize değerini küçülterek 'Bus Error' riskini sıfırlıyoruz
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=65536)
    buffer = b""
    prev_time = 0
    deadzone = 0.12 

    print("El takip sistemi baslatiliyor...")

    try:
        while True:
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            buffer += chunk

            a = buffer.find(b'\xff\xd8')
            b = buffer.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = buffer[a:b+2]
                buffer = buffer[b+2:]
                
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    continue

                frame = cv2.flip(frame, 1)
                h, w, c = frame.shape
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                pan_komut = 96
                tilt_komut = 96

                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    bilek = hand_landmarks.landmark[0] 

                    # --- PAN (GPIO 18) ---
                    if bilek.x > 0.5 + deadzone:
                        pan_komut = 105   
                    elif bilek.x < 0.5 - deadzone:
                        pan_komut = 87    
                    else:
                        pan_komut = 96    

                    # --- TILT (GPIO 19) ---
                    if bilek.y < 0.5 - deadzone:
                        tilt_komut = 105  
                    elif bilek.y > 0.5 + deadzone:
                        tilt_komut = 87   
                    else:
                        tilt_komut = 96   

                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # ESP32'ye komut fırlat
                veri_paketi = f"{pan_komut},{tilt_komut}\n"
                esp32.write(veri_paketi.encode('utf-8'))

                # FPS Ekranı
                curr_time = time.time()
                fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
                prev_time = curr_time

                cv2.putText(frame, f"FPS: {int(fps)} | P: {pan_komut} | T: {tilt_komut}", (15, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Merkez Çizgileri
                cv2.line(frame, (int(w/2), 0), (int(w/2), h), (255, 0, 0), 1)
                cv2.line(frame, (0, int(h/2)), (w, int(h/2)), (255, 0, 0), 1)

                cv2.imshow("Pi 5 - Pan-Tilt El Takip", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Hata: {e}")
    finally:
        try:
            esp32.write(b"96,96\n")
            esp32.close()
        except:
            pass
        process.terminate()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()