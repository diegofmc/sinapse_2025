#Modules
#Data Base
import model
import data_base
from model import Db_information
from model import Config_install
from model import Registro
from model import Registro_sensor
from model import registro_instalacao
import json

#Hardware
from leitor_termo import Leitor_temp
from multiplex import Multiplex

#date time
import time
from datetime import date
from datetime import datetime

#Read configuration installation
db = Db_information("Termometria",3306,"localhost","leitor_termo","termometria")
conn = data_base.Connector(db)
conf = conn.get_informaton_instal()
data_instal = json.loads(conf.dados)

canais = data_instal["Cordoes"]
sensores = []
for key in data_instal.keys():
    sensores.append(data_instal[key])
sensores.pop(0)

#initialization hardware
leitor = Leitor_temp()
mp = Multiplex()

#bool var start reading
enable_read_loop = True
read_temp = True
key = ""
key_sensor = ""
value = ""
dt = datetime
value_sensor = 0.0

#Registro
data_temp = {}
record_sensor = Registro_sensor(dt.now(), dt.now(), "", 1, 0.0)
registro_instal = registro_instalacao(0, conf.nome, conf.configuracao_fisica, dt.now(), "")
# Função para validar leituras e calcular a média
def process_sensor_readings(sensor_readings):
    # Filtra leituras válidas dentro do intervalo de 10°C a 65°C
    valid_readings = [r for r in sensor_readings if 10 <= r <= 65]
    if len(valid_readings) == 3:
        # Média de 3 leituras válidas
        return sum(valid_readings) / 3
    elif len(valid_readings) == 2:
        # Média de 2 leituras válidas
        return sum(valid_readings) / 2
    elif len(valid_readings) == 1:
        # Retorna a única leitura válida
        return valid_readings[0]
    else:
        # Nenhuma leitura válida, retorna valor padrão
        return None

# Inicializa a coleta de dados
while enable_read_loop:
    time.sleep(0.001)
    if dt.now().minute == 0 and dt.now().second < 5 and read_temp == False:
        read_temp = True

    if read_temp:
        data_temp.clear()
        for canal in range(canais):
            for sensor in range(sensores[canal]):
                mp.set_canal(canal + 1)
                mp.set_sensor(sensor + 1)
                time.sleep(0.00001)

                # Realiza 3 leituras consecutivas
                readings = []
                for _ in range(3):
                    value_sensor = leitor.read_temp()
                    readings.append(value_sensor)
                    time.sleep(0.00003)

                # Processa as leituras para validar e calcular a média
                average_value = process_sensor_readings(readings)
                
                # Se nenhuma leitura for válida, atribui um valor padrão (opcional)
                if average_value is None:
                    average_value = 0.0

                # Formata e salva os dados
                key = f"Ch{canal + 1}S{sensor + 1}"
                key_sensor = f"CL3/SL18/CO{canal + 1}/S{sensor + 1}"
                value = "{:.2f}".format(average_value)
                
                # Armazena os dados no dicionário
                data_temp[key] = value

                # Atualiza o registro do sensor no banco
                record_sensor.created_at = dt.now()
                record_sensor.data_hora = dt.now()
                record_sensor.tag = key_sensor
                record_sensor.tipo = 1
                record_sensor.valor = average_value
                conn.insert_record_sensor(record_sensor)

        # Atualiza o registro de instalação
        registro_instal.registros_temperaturas = json.dumps(data_temp)
        registro_instal.data = dt.now()
        conn.insert_registro_instalacao(registro_instal)
        
        read_temp = False
