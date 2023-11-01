import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
import os
import psycopg2
import time

# Configurações para conexão com PostgreSQL
DB_HOST = "127.0.0.1"
DB_PORT = "5433"
DB_NAME = "db_skymapping"
DB_USER = "postgres"
DB_PASS = "20010510"

# Conectar ao PostgreSQL
conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
cursor = conn.cursor()

# Inicialize o detector de corpo do MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

video_capture = cv2.VideoCapture(0)  # Índice 0 para webcam padrão

# Definir fps para 30
fps = 30
video_capture.set(cv2.CAP_PROP_FPS, fps)

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('temp_video.avi', fourcc, fps, (int(video_capture.get(3)), int(video_capture.get(4))))

time_detected = None
video_started = False

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        if time_detected is None:
            time_detected = time.time()

        if time.time() - time_detected > 5 and not video_started:
            video_started = True

        if video_started:
            out.write(frame)

        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_as_bytes = img_encoded.tobytes()

        cursor.execute("INSERT INTO detected_images (image, timestamp) VALUES (%s, %s)", (img_as_bytes, current_time_str))
        conn.commit()

    else:
        if video_started:
            out.release()
            with open('temp_video.avi', 'rb') as f:
                video_as_bytes = f.read()
                cursor.execute("INSERT INTO detected_videos (video, timestamp) VALUES (%s, %s)", (video_as_bytes, current_time_str))
                conn.commit()
            video_started = False
        time_detected = None

    cv2.imshow('Pose Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

if video_started:
    out.release()

video_capture.release()
cv2.destroyAllWindows()
cursor.close()
conn.close()

