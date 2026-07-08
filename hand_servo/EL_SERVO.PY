import cv2
import serial
import time
import mediapipe as mp

# ESP32 Port Kontrolü (Gerekirse COM4 yapın)
try:
    esp32 = serial.Serial(port='COM4', baudrate=115200, timeout=0.1)
    print("ESP32 bağlantısı başarılı.")
    time.sleep(2) 
except Exception as e:
    print(f"ESP32'ye bağlanılamadı! Portu kontrol edin. Hata: {e}")
    exit()

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)

# El merkezden ne kadar uzaklaşınca motor dönsün? (Esneklik payı)
deadzone = 0.1 

print("Sistem kalibre edilmiş olarak çalışıyor. Çıkmak için 'q'ya basın.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Varsayılan olarak motorları DURDUR (Yeni sihirli sayı: 96)
    pan_komut = 96
    tilt_komut = 96

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
            el_etiketi = hand_info.classification[0].label
            bilek = hand_landmarks.landmark[0] 
            
            if el_etiketi == "Right":
                # SAĞ EL -> YATAY HAREKET (X Ekseni)
                if bilek.x > 0.5 + deadzone:
                    pan_komut = 105  # Sağa yavaşça dön
                elif bilek.x < 0.5 - deadzone:
                    pan_komut = 87   # Sola yavaşça dön (96 - 9 = 87)
                else:
                    pan_komut = 96   # Merkezde zınk diye dur
                
            elif el_etiketi == "Left":
                # SOL EL -> DİKEY HAREKET (Y Ekseni)
                if bilek.y < 0.5 - deadzone:
                    tilt_komut = 105 # Yukarı yavaşça dön
                elif bilek.y > 0.5 + deadzone:
                    tilt_komut = 87  # Aşağı yavaşça dön
                else:
                    tilt_komut = 96  # Merkezde zınk diye dur

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # ESP32'ye kalibre edilmiş veriyi gönder
    veri_paketi = f"{pan_komut},{tilt_komut}\n"
    esp32.write(veri_paketi.encode('utf-8'))
        
    cv2.putText(frame, f"Pan Motoru: {pan_komut}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Tilt Motoru: {tilt_komut}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Merkez çizgileri
    cv2.line(frame, (int(w/2), 0), (int(w/2), h), (255, 0, 0), 1)
    cv2.line(frame, (0, int(h/2)), (w, int(h/2)), (255, 0, 0), 1)

    cv2.imshow('360 Servo Hand Control', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
esp32.close()