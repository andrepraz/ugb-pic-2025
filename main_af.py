import network
import socket
from machine import Pin, PWM

# Configuração dos servos para cada dedo
# Ajuste os pinos conforme seu hardware
servos = {
    "Polegar": PWM(Pin(25, mode=Pin.OUT)),
    "Indicador": PWM(Pin(26, mode=Pin.OUT)),
    "Medio": PWM(Pin(27, mode=Pin.OUT)),
    "Anelar": PWM(Pin(14, mode=Pin.OUT)),
    "Minimo": PWM(Pin(12, mode=Pin.OUT))
}

for servo in servos.values():
    servo.freq(50)

# Funções para mover servos
def mover_dedo(dedo, estado):
    if dedo not in servos:
        print(f"Dedo desconhecido: {dedo}")
        return

    if estado == "Aberto":
        servos[dedo].duty(26)  # posição aberta
    elif estado == "Fechado":
        servos[dedo].duty(80)  # posição fechada
    else:
        print(f"Estado desconhecido: {estado}")

# Desativa AP anterior e cria novo
ap = network.WLAN(network.AP_IF)
if ap.active():
    ap.active(False)

ap.active(True)
ap.config(essid='ESP32_AP', password='Esp32@ap')
ap.config(authmode=network.AUTH_WPA_WPA2_PSK)

print('Ponto de Acesso criado!')
print('SSID:', ap.config('essid'))
print('Endereço IP:', ap.ifconfig()[0])

# Configurar servidor socket
port = 80
addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Servidor escutando na porta', port)

# Loop principal
try:
    while True:
        conn, addr = s.accept()
        print('Conexão recebida de', addr)

        data = conn.recv(1024)
        if data:
            message = data.decode().strip()
            print("Mensagem recebida:", message)

            # Espera formato "<dedo>:<estado>"
            if ":" in message:
                dedo, estado = message.split(":", 1)
                mover_dedo(dedo, estado)
            else:
                print("Formato inválido:", message)

            conn.sendall(f"Mensagem recebida: {message}".encode())

        conn.close()

except KeyboardInterrupt:
    ap.active(False)
    print("Ponto de Acesso desligado.")
