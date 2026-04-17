import cv2
import numpy as np
import threading
import time
import subprocess
import os

# Global alarm control
ALARM_PROCESS = None
ALARM_ON = False

def play_single_alarm():
    global ALARM_PROCESS, ALARM_ON
    if ALARM_PROCESS is None or ALARM_PROCESS.poll() is not None:
        # Play ONCE and wait complete
        ALARM_PROCESS = subprocess.Popen(['start', '/wait', 'alarm.mp3'], 
                                        shell=True, stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
        print("🔊 ALARM PLAYING... (full length)")
    
    ALARM_PROCESS.wait()  # Wait for complete
    ALARM_PROCESS = None

# Load cascades
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

EYE_CLOSED_FRAMES = 120
COUNTER = 0

cap = cv2.VideoCapture(0)
print("Driver System ON! Close eyes 3-4 sec = FULL ALARM ONCE")

while True:
    ret, frame = cap.read()
    if not ret: break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (450, 300))
    frame = cv2.resize(frame, (450, 300))

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray)
        
        if len(eyes) == 0:
            COUNTER += 1
            cv2.putText(frame, f"CLOSED: {COUNTER}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            COUNTER = 0
            cv2.putText(frame, "EYES OPEN ✓", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame[y:y+h, x:x+w], (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

        # ALARM: Play FULL once every time condition met
        if COUNTER >= EYE_CLOSED_FRAMES:
            if not ALARM_ON:
                print("🚨 DROWSY! FULL ALARM START 🚨")
                ALARM_ON = True
                # New thread for NON-BLOCKING full play
                t = threading.Thread(target=play_single_alarm)
                t.daemon = True
                t.start()
            
            cv2.putText(frame, "🚨 FULL ALARM ON 🚨", (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        else:
            ALARM_ON = False

    cv2.imshow('Spark Driver Alert System', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()