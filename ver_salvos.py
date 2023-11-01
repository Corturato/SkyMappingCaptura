import cv2
import psycopg2
import numpy as np
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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

# Função para exibir imagens
def display_image(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow('Selected Image', img_np)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Função para exibir vídeos
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

# Funções de callback para os botões
def view_images():
    cursor.execute("SELECT id, timestamp FROM detected_images")
    rows = cursor.fetchall()
    if not rows:
        status_label.config(text="Nenhuma imagem encontrada.")
        return

    status_label.config(text="selecione uma imagem para ver.")
    image_list.delete(0, tk.END)

    for row in rows:
        image_list.insert(tk.END, f"ID: {row[0]}, Tempo: {row[1]}")

def view_videos():
    cursor.execute("SELECT id, timestamp FROM detected_videos")
    rows = cursor.fetchall()
    if not rows:
        status_label.config(text="Nenhum vídeo encontrado.")
        return

    status_label.config(text="Selecione um vídeo para ver.")
    video_list.delete(0, tk.END)

    for row in rows:
        video_list.insert(tk.END, f"ID: {row[0]}, Tempo: {row[1]}")

def view_selected_image():
    selected_image = image_list.get(image_list.curselection())
    img_id = selected_image.split("ID: ")[1].split(",")[0]

    cursor.execute("SELECT image FROM detected_images WHERE id = %s", (img_id,))
    img_data = cursor.fetchone()
    if img_data:
        display_image(img_data[0])
    else:
        status_label.config(text="Imagem não encontrada.")

def view_selected_video():
    selected_video = video_list.get(video_list.curselection())
    video_id = selected_video.split("ID: ")[1].split(",")[0]

    cursor.execute("SELECT video FROM detected_videos WHERE id = %s", (video_id,))
    video_data = cursor.fetchone()
    if video_data:
        display_video(video_data[0])
    else:
        status_label.config(text="Video não encontrado.")

# Criar a janela principal
root = tk.Tk()
root.title("Visualizador do SkyMapping")

# Criar frames
frame_images = ttk.LabelFrame(root, text="Imagens")
frame_images.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
frame_videos = ttk.LabelFrame(root, text="Vídeos")
frame_videos.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
frame_status = ttk.LabelFrame(root, text="Status")
frame_status.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Criar listas para exibir imagens e vídeos
image_list = tk.Listbox(frame_images, selectmode=tk.SINGLE)
image_list.pack(fill=tk.BOTH, expand=True)
video_list = tk.Listbox(frame_videos, selectmode=tk.SINGLE)
video_list.pack(fill=tk.BOTH, expand=True)

# Botões
btn_view_images = ttk.Button(frame_images, text="Carregar imagens", command=view_images)
btn_view_images.pack()
btn_view_videos = ttk.Button(frame_videos, text="Carregar vídeos", command=view_videos)
btn_view_videos.pack()

# Botão para visualizar imagem selecionada
btn_view_selected_image = ttk.Button(frame_images, text="Ver imagem selecionada", command=view_selected_image)
btn_view_selected_image.pack()
btn_view_selected_video = ttk.Button(frame_videos, text="Ver vídeo selecionado", command=view_selected_video)
btn_view_selected_video.pack()

# Rótulo de status
status_label = ttk.Label(frame_status, text="")
status_label.pack()

# Configuração das colunas e linhas da grade
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# Iniciar a interface gráfica
root.mainloop()

# Fechar a conexão com o PostgreSQL
cursor.close()
conn.close()
