# Rodando o projeto
- Primeiro, instale o gerenciador de pacotes do python uv: https://github.com/astral-sh/uv
- Entre no diretório do projeto e rode o comando 'uv sync' para instalar as dependências
- Inicie o kafka e a sua interface gráfica rodando 'docker compose -f ./compose.yaml up -d'
- Inicie o broker rodando 'uv run broker/main.py'
- Inicie o backend usando
    - 'cd app'
    - 'uv run fastapi dev'
- Inicie o ar condicioando usando
    - 'cd devices'
    - 'uv run air_conditioning.py'

# Como funciona:
- Os dispositivos enviam periodicamente sinais de vida para o backend, que, periodicamente
remove da lista de dispositivos os dispositivos que estao a mais de X segundos sem enviar
sinais.
- O backend tem chamadas para listar o estado dos dispositivos e para enviar comandos aos mesmos
- Para listar os dispositivos basta dar um GET em /device
- Para enviar comandos para dar um POST em /control_device
    - O post recebe tres parametros: o nome do comando, uma lista com inteiros contendo os parametros
    (se o comando precisar de parametros, por exemplo, TURN_OFF nao precisa, ao mesmo
    tempo que CHANGE_COLOR precisa, que sao as cores da cor nova),
    - Exemplo: { "device_id: "1231234123", "name": "CHANGE_COLOR", "params": [255, 255, 255] }
    - Exemplo: { "device_id: "1231234123", "name": "TURN_OFF" }
- Seria interessante fazer com que o cliente recupere periodicamente o estado dos dispositivos
- Quando os dispositivos estiverem desligados, impedir que o estado dele seja alterado, por exemplo,
impedir que o ar condicionado tenha sua temperatura aumentada pelo cliente quando ele estiver desligado

- Comandos que o ar concidionado aceita:
    - TURN_ON
    - TURN_OFF
    - INCREASE_TEMPERATURE
    - DECREASE_TEMPERATURE

- Comandos que a lampada aceita:
    - TURN_ON
    - TURN_OFF
    - CHANGE_COLOR
        - Recebe como parametro tres valores, R, G e B, exemplo: [255, 123, 111]

- Comandos que o radio aceita:
    - TURN_ON
    - TURN_OFF
    - CHANGE_MUSIC
        - Recebe como parametro um numero de 0 a 9, que serao os indices das musicas disponiveis

- OBS: Mais de um dispositivo do mesmo tipo pode se conectar, pois eles podem ter Nomes e ids diferentes
