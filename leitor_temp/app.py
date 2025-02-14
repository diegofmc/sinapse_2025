from flask import Flask, jsonify, send_from_directory
import board
import digitalio
import adafruit_max31856
import time
import json
import threading
from datetime import datetime
import os

# Caminho para a pasta onde os arquivos HTML e JS estão
DADOS_PATH = os.path.join(os.getcwd(), "dados")

# Inicializa o Flask
app = Flask(__name__, static_folder=DADOS_PATH)

# Tenta inicializar Multiplex3 sem travar o sistema
try:
    from multiplex import Multiplex3
    mp = Multiplex3()
except OSError as e:
    print(f"Erro ao inicializar Multiplex3: {e}")
    mp = None  # Evita falha total no código

# Configuração do SPI e sensor
spi = board.SPI()
cs = digitalio.DigitalInOut(board.PA7)
cs.direction = digitalio.Direction.OUTPUT
thermocouple = adafruit_max31856.MAX31856(spi, cs)

DATA_FILE = "leituras.json"
INTERVALO_COLETA = 5  # Tempo entre coletas (segundos)

# Variável global para armazenar o canal atual
CANAL_ATUAL = 3  # Inicia com o canal 3

@app.route('/')
def index():
    """Serve a página principal index.html a partir da pasta dados."""
    return send_from_directory(DADOS_PATH, "index.html")

@app.route('/script.js')
def script():
    """Serve o arquivo script.js a partir da pasta dados."""
    return send_from_directory(DADOS_PATH, "script.js")

@app.route('/dados')
def get_dados():
    """Retorna os dados salvos em leituras.json."""
    try:
        with open(DATA_FILE, "r") as f:
            dados = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        dados = []

    return jsonify(dados)

@app.route('/mudar_canal/<int:canal>')
def mudar_canal(canal):
    """Muda o canal, atualiza a variável e força uma nova leitura."""
    global CANAL_ATUAL
    CANAL_ATUAL = canal

    if mp:
        mp.set_canal(canal)

    print(f"Canal alterado para {canal}. Atualizando leitura...")
    return forcar_leitura()

@app.route('/forcar_leitura')
def forcar_leitura():
    """Força uma nova leitura e atualiza o arquivo JSON."""
    sensores = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sensor = 1
    while sensor <= 16:
        if mp:
            mp.set_canal(CANAL_ATUAL)
            mp.set_sensor(sensor)

        time.sleep(0.2)

        try:
            temp = thermocouple.temperature
            if temp is None:
                raise ValueError("Leitura inválida")
        except Exception as e:
            temp = "Erro"
            print(f"Erro ao ler sensor {sensor}: {e}")

        sensores.append({
            'sensor': sensor,
            'canal': CANAL_ATUAL,
            'temperatura': temp,
            'data_hora': timestamp
        })

        sensor += 1

    salvar_dados(sensores)
    print(f"[{timestamp}] Canal {CANAL_ATUAL} - Leitura Atualizada!")
    return jsonify({"mensagem": "Leitura forçada com sucesso!"})

def salvar_dados(novas_leituras):
    """Salva os dados no arquivo JSON, mantendo somente a última leitura."""
    with open(DATA_FILE, "w") as f:
        json.dump(novas_leituras, f, indent=4)

def coleta_automatica():
    """Executa a coleta de dados em loop, a cada INTERVALO_COLETA segundos."""
    while True:
        sensores = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sensor = 1
        while sensor <= 16:
            if mp:
                mp.set_canal(CANAL_ATUAL)
                mp.set_sensor(sensor)
            time.sleep(0.2)
            try:
                temp = thermocouple.temperature
                if temp is None:
                    raise ValueError("Leitura inválida")
            except Exception as e:
                temp = "Erro"
                print(f"Erro ao ler sensor {sensor}: {e}")

            sensores.append({
                'sensor': sensor,
                'canal': CANAL_ATUAL,
                'temperatura': temp,
                'data_hora': timestamp
            })
            sensor += 1

        salvar_dados(sensores)
        print(f"[{timestamp}] Canal {CANAL_ATUAL} - Coleta automática realizada!")
        time.sleep(INTERVALO_COLETA)

# Inicia a coleta automática em uma thread separada
threading.Thread(target=coleta_automatica, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500)
