import network
import socket
import time
from machine import Pin, PWM

servo3 = PWM(Pin(25, mode=Pin.OUT))
servo3.freq(50)

# Desativa o AP anterior, se estiver ativo
ap = network.WLAN(network.AP_IF)
if ap.active():
  ap.active(False)

# Configurar o modo Access Point
ap.active(True)
ap.config(essid='ESP32_AP', password='Esp32@ap')
ap.config(authmode=network.AUTH_WPA_WPA2_PSK)

# Exibir informações do ponto de acesso
print('Ponto de Acesso criado!')
print('SSID:', ap.config('essid'))
#print('Senha:', ap.config('password'))
print('Endereço IP:', ap.ifconfig()[0])

# Configurar servidor para escutar conexcoes
port = 80
#addr = socket.getaddrinfo('0.0.0.0', port)[0]
addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
print('addr', addr[0])
s = socket.socket()
s.bind(addr)
s.listen(1)

print('Servidor escutando na porta', port)

# Loop para manter o código em execução
try:
    while True:
        conn, addr = s.accept()
        print('Conexão recebida de', addr)

        # Receber dados do cliente
        data = conn.recv(1024)
        if data:
          message = data.decode()
          print(message)
          if message == '4':
            servo3.duty(26)
            
          else:
            servo3.duty(80)
            
            print("Mensagem recebida do cliente:", message)

            # Resposta ao cliente
            response = "Mensagem recebida: " + message
            conn.sendall(response.encode())

        conn.close()
except KeyboardInterrupt:
    ap.active(False)  # Desativa o AP ao sair
    print("Ponto de Acesso desligado.")