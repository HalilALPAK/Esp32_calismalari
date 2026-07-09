# -*- coding: utf-8 -*-
import cv2
import numpy as np
import subprocess
import time
import serial

def main():
    # --- ESP32 Bağlantısı ---
    try:
        esp32 = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=0.1)
        print("ESP32 baglantisi basarili.")
        time.sleep(2)
    except Exception as e:
        print(f"ESP32 port hatasi! Hata: {e}")
        return

    # --- Optimize rpicam-vid Komutu ---
    command = [
        'rpicam-vid', '--camera', '0', '--width', '480', '--height', '480',
        '--codec', 'mjpeg', '--inline', '--timeout', '0', '--nopreview', 
        '--flush', '--framerate', '30', '-o', '-'
    ]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=65536)
    buffer = b""
    prev_time = 0
    deadzone = 0.12 

    # --- Ten Rengi Algılama Parametreleri (YCrCb Renk Uzayı) ---
    min_YCrCb = np.array([0, 133, 77], np.uint8)
    max_YCrCb = np.array([255, 173, 127], np.uint8)

    print("Ten rengi ile el takip sistemi baslatildi. Cikmak icin 'q'ya basin.")

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
                
                ycrcb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                mask = cv2.inRange(ycrcb_frame, min_YCrCb, max_YCrCb)
                
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                mask = cv2.erode(mask, kernel, iterations=2)
                mask = cv2.dilate(mask, kernel, iterations=2)
                mask = cv2.GaussianBlur(mask, (3, 3), 0)

                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                pan_komut = 96
                tilt_komut = 96

                if contours:
                    en_buyuk_kontur = max(contours, key=cv2.contourArea)
                    
                    if cv2.contourArea(en_buyuk_kontur) > 1200:
                        M = cv2.moments(en_buyuk_kontur)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            
                            norm_cX = cX / w
                            norm_cY = cY / h

                            # --- PAN (GPIO 18) ---
                            if norm_cX > 0.5 + deadzone:
                                pan_komut = 105   
                            elif norm_cX < 0.5 - deadzone:
                                pan_komut = 87    
                            else:
                                pan_komut = 96    

                            # --- TILT (GPIO 19) ---
                            if norm_cY < 0.5 - deadzone:
                                tilt_komut = 105  
                            elif norm_cY > 0.5 + deadzone:
                                tilt_komut = 87   
                            else:
                                tilt_komut = 96   

                            cv2.circle(frame, (cX, cY), 8, (0, 255, 0), -1)
                            x, y, w_b, h_b = cv2.boundingRect(en_buyuk_kontur)
                            cv2.rectangle(frame, (x, y), (x + w_b, y + h_b), (0, 255, 0), 2)

                # --- ESP32'ye Veri Gönder ---
                veri_paketi = f"{pan_komut},{tilt_komut}\n"
                esp32.write(veri_paketi.encode('utf-8'))

                curr_time = time.time()
                fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
                prev_time = curr_time

                cv2.putText(frame, f"FPS: {int(fps)} | P: {pan_komut} | T: {tilt_komut}", (15, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                cv2.line(frame, (int(w/2), 0), (int(w/2), h), (255, 0, 0), 1)
                cv2.line(frame, (0, int(h/2)), (w, int(h/2)), (255, 0, 0), 1)

                cv2.imshow("Pi 5 - Kesintisiz El Takip", frame)

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