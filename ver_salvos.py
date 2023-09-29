import cv2
import psycopg2
import numpy as np
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
fps = 30  # taxa de quadros definida durante a gravação
frame_duration = 1.0 / fps

def display_image(img_bytes):
    # Converta bytes em uma matriz numpy e depois em uma imagem
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow('Selected Image', img_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def display_video(video_bytes):
    temp_file = "temp_video_playback.avi"
    with open(temp_file, 'wb') as f:
        f.write(video_bytes)
    
    cap = cv2.VideoCapture(temp_file)
    
    last_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        elapsed_time = current_time - last_time

        if elapsed_time < frame_duration:
            time.sleep(frame_duration - elapsed_time)

        cv2.imshow('Selected Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        last_time = current_time

    cap.release()
    cv2.destroyAllWindows()

while True:
    print("1. View Images")
    print("2. View Videos")
    print("3. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        cursor.execute("SELECT id, timestamp FROM detected_images")
        rows = cursor.fetchall()
        if not rows:
            print("No images found.")
            continue
        
        for row in rows:
            print(f"ID: {row[0]}, Timestamp: {row[1]}")
        
        img_id = input("Enter the ID of the image you want to view: ")
        
        cursor.execute("SELECT image FROM detected_images WHERE id = %s", (img_id,))
        img_data = cursor.fetchone()
        if img_data:
            display_image(img_data[0])
        else:
            print("Image not found.")

    elif choice == '2':
        cursor.execute("SELECT id, timestamp FROM detected_videos")
        rows = cursor.fetchall()
        if not rows:
            print("No videos found.")
            continue
        
        for row in rows:
            print(f"ID: {row[0]}, Timestamp: {row[1]}")
        
        video_id = input("Enter the ID of the video you want to view: ")
        
        cursor.execute("SELECT video FROM detected_videos WHERE id = %s", (video_id,))
        video_data = cursor.fetchone()
        if video_data:
            display_video(video_data[0])
        else:
            print("Video not found.")

    elif choice == '3':
        break

cursor.close()
conn.close()