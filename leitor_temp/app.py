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
app = Flask(__name__, static_folder=DADOS_PATH, template_folder=DADOS_PATH)

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
    """Serve a página principal `index.html` diretamente da pasta `dados/`"""
    return send_from_directory(DADOS_PATH, "index.html")

@app.route('/script.js')
def script():
    """Serve o `script.js` para a página"""
    return send_from_directory(DADOS_PATH, "script.js")

@app.route('/dados')
def get_dados():
    """Retorna os dados salvos em `leituras.json`"""
    try:
        with open(DATA_FILE, "r") as f:
            historico = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        historico = []

    return jsonify(historico)

@app.route('/mudar_canal/<int:canal>')
def mudar_canal(canal):
    """Muda o canal e força uma nova leitura"""
    global CANAL_ATUAL
    CANAL_ATUAL = canal

    if mp:
        mp.set_canal(canal)

    return jsonify({"mensagem": f"Canal alterado para {canal}"})


def salvar_dados(dados):
    """Salva os dados no arquivo JSON, sempre sobrescrevendo."""
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f, indent=4)


def coletar_dados():
    """Evita reinicializações inesperadas e coleta os dados continuamente"""
    while True:
        try:
            sensores = []
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            sensor = 1  # Sempre começa do sensor 1

            while sensor <= 16:
                if mp:  # Apenas se Multiplex3 estiver inicializado
                    mp.set_canal(CANAL_ATUAL)  # Usa a variável global
                    mp.set_sensor(sensor)

                time.sleep(0.2)  # Reduzido para evitar travamento

                try:
                    temp = thermocouple.temperature
                except Exception as e:
                    temp = None
                    print(f"Erro ao ler sensor {sensor}: {e}")

                sensores.append({
                    'sensor': sensor,
                    'canal': CANAL_ATUAL,
                    'temperatura': temp if temp is not None else "Erro",
                    'data_hora': timestamp
                })

                sensor += 1

            salvar_dados(sensores)  # Agora os dados são sobrescritos
            print(f"[{timestamp}] Canal {CANAL_ATUAL} - Dados coletados!")  # Log no terminal

            time.sleep(INTERVALO_COLETA)

        except Exception as e:
            print(f"Erro crítico na coleta de dados: {e}")
            time.sleep(5)  # Aguarda antes de tentar novamente

# Iniciar a coleta automática em uma thread separada
threading.Thread(target=coletar_dados, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=500)
