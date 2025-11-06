import socket
import time
import cv2
import mediapipe as mp
import logging
import os
import threading
from datetime import datetime

# Configuração da captura de vídeo
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_V4L2)
cap.set(3, 640)  # Largura
cap.set(4, 480)  # Altura

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2,
                      min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

ESP32_IP = '192.168.4.1'
PORT = 80

# Estado anterior de cada dedo
previous_fingers_state = [None] * 5  # Polegar, indicador, médio, anelar, mínimo

# Nome dos dedos
finger_names = ["Polegar", "Indicador", "Medio", "Anelar", "Minimo"]

def send_message_to_esp32(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ESP32_IP, PORT))
            s.sendall(message.encode())
            #response = s.recv(1024)
            #print("Recebido do ESP32:", response.decode())
    except ConnectionRefusedError:
        print("Falha na conexão. Verifique se o ESP32 está ativo e escutando.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            # Landmarks para cada dedo
            finger_tips = [4, 8, 12, 16, 20]   # Polegar, Indicador, Médio, Anelar, Mínimo
            finger_mcp  = [2, 5, 9, 13, 17]    # MCP ou articulação base

            # Detectar se cada dedo está aberto (tip < mcp => aberto)
            for i, (tip_id, mcp_id) in enumerate(zip(finger_tips, finger_mcp)):
                is_open = handLms.landmark[tip_id].y < handLms.landmark[mcp_id].y
                state = "Aberto" if is_open else "Fechado"

                # Só envia se houve mudança no estado do dedo
                if previous_fingers_state[i] != state:
                    previous_fingers_state[i] = state
                    message = f"{finger_names[i]}:{state}"
                    threading.Thread(target=send_message_to_esp32, args=(message,)).start()

                # Escreve na tela o estado de cada dedo
                cv2.putText(img, f"{finger_names[i]}: {state}",
                            (10, 30 + i * 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
