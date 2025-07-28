import socket
import time
import cv2
import mediapipe as mp
import logging
import os
import threading
from datetime import datetime

# Configuração do log
year, month, day = datetime.now().year, datetime.now().month, datetime.now().day
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', str(year), str(month), str(day))
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=os.path.join(log_dir, 'braco2v1.2.log'), level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

# Configuração da captura de vídeo
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_V4L2)
cap.set(3, 640)  # Largura
cap.set(4, 480)  # Altura

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

ESP32_IP = '192.168.4.1'
PORT = 80

previous_state = None

def send_message_to_esp32(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ESP32_IP, PORT))
            s.sendall(message.encode())
            response = s.recv(1024)
            print("Recebido do ESP32:", response.decode())
    except ConnectionRefusedError:
        print("Falha na conexão. Verifique se o ESP32 está ativo e escutando.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

while True:
    success, img = cap.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            # Obter as posições dos pontos relevantes
            tips_y = [handLms.landmark[i].y for i in [8, 12, 16, 20]]  # Pontas dos dedos
            mcp_y = [handLms.landmark[i].y for i in [5, 9, 13, 17]]   # Articulações

            # Verificar se as pontas dos dedos estão acima das articulações
            tips_above_mcp = [tip < mcp for tip, mcp in zip(tips_y, mcp_y)]

            if all(tips_above_mcp):
                new_state = '0'  # Mão aberta
            elif not any(tips_above_mcp):
                new_state = '4'  # Mão fechada
            else:
                new_state = 'fora de padrão'  # Mão fora de padrão

            # Enviar mensagem ao ESP32 se o estado mudou
            if new_state != previous_state:
                previous_state = new_state
                threading.Thread(target=send_message_to_esp32, args=(new_state,)).start()

            # Exibir informação na tela
            if new_state == '4':
                cv2.putText(img, 'Mao Fechada', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            elif new_state == '0':
                cv2.putText(img, 'Mao Aberta', (10, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            else:
                cv2.putText(img, 'Mao Fora de Padrao', (10, 170), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()