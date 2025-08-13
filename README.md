# PROTÓTIPO DE MOVIMENTAÇÃO DO BRAÇO ROBÓTICO COM CONTROLE DE MÃO VIA WI-FI E MEDIAPIPE
O objetivo é desenvolver um sistema integrado que permita o controle do braço robótico e da mão através de gestos reconhecidos por um sistema de visão computacional, utilizando Python, OpenCV e ESP32 para comunicação sem fio.

# main.py
O arquivo main.py contém o código que chamamos de Access Point (AP) - Um ponto de acesso sem fio (em inglês: wireless access point, sigla WAP) é um dispositivo em uma rede sem fio que realiza a interconexão entre todos os dispositivos móveis. Está embutido no Esp32 para emitir acesso wi-fi para os cliente. Sua conexão dependem de senha para acesso.

# cliente_esp32_deteccao.py
Este arquigo contém uma aplicação para detectar o movimento dos dedos da mão e passa o sinal para o AP que movimentará a mão.

# uso do Git
```
> git status
```