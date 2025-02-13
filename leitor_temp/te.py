from pymodbus.client import ModbusTcpClient
import time

# Defina o IP e a porta do servidor
SERVER_IP = '192.168.1.203'  # Substitua pelo IP do servidor
SERVER_PORT = 502

# Cria um cliente Modbus
client = ModbusTcpClient(SERVER_IP, port=SERVER_PORT)

def write_data(temperature, humidity):
    # Conecta ao servidor
    if client.connect():
        print("Conectado ao servidor Modbus!")

        # Escreve a temperatura (supondo que é escrita no registrador 0)
        temp_register = int(temperature * 10)  # Multiplicando por 10 para ajustar a escala
        result_temp = client.write_register(0, temp_register)

        # Escreve a umidade (supondo que é escrita no registrador 1)
        humidity_register = int(humidity * 10)  # Multiplicando por 10 para ajustar a escala
        result_humidity = client.write_register(1, humidity_register)

        if result_temp.isError() or result_humidity.isError():
            print("Erro ao escrever nos registradores.")
        else:
            print(f"Temperatura escrita: {temperature} °C, Umidade escrita: {humidity} %")

        # Desconecta do servidor
        client.close()
    else:
        print("Não foi possível conectar ao servidor Modbus.")

if __name__ == "__main__":
    while True:
        # Simula leitura de dados do PLC
        temperature = float(input("Insira a temperatura ambiente em °C: "))
        humidity = float(input("Insira a umidade relativa em %: "))

        write_data(temperature, humidity)

        # Espera 5 segundos antes de pedir novos dados
        time.sleep(5)
