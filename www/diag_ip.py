import time
import socket
import subprocess
import re

# Definição dos LEDs
LED_GREEN = "/sys/class/leds/orangepi:green:pwr/brightness"  # LED Verde (Início e separação)
LED_RED = "/sys/class/leds/orangepi:red:status/brightness"  # LED Vermelho (Piscando os números)


# Obtém o endereço IP dinâmico da interface 'end0'
def get_local_ip():
    interface_name = "end0"  # Interface desejada
    try:
        # Executa o comando para obter os detalhes da interface
        output = subprocess.check_output(
            ["ip", "-o", "addr", "show", "dev", interface_name],
            encoding="utf-8"
        )
        # Primeiro, procura por uma linha que contenha "inet" e "dynamic"
        for line in output.splitlines():
            if "inet " in line and "dynamic" in line:
                # Usa expressão regular para extrair o IP (antes da barra)
                m = re.search(r'inet ([0-9\.]+)/', line)
                if m:
                    return m.group(1)
        # Se não encontrou um IP dinâmico, retorna o primeiro IP encontrado (fallback)
        for line in output.splitlines():
            if "inet " in line:
                m = re.search(r'inet ([0-9\.]+)/', line)
                if m:
                    return m.group(1)
        return "0.0.0.0"  # Caso nenhum IP seja encontrado
    except subprocess.CalledProcessError:
        return "0.0.0.0"
    except Exception as e:
        print(f"Erro ao obter IP: {e}")
        return "0.0.0.0"


# Função para piscar um LED específico
def set_led(led_path, state, duration=0.4):
    try:
        with open(led_path, "w") as led_file:
            led_file.write(str(state))
    except Exception as e:
        print(f"Erro ao escrever no LED {led_path}: {e}")
    time.sleep(duration)
    try:
        with open(led_path, "w") as led_file:
            led_file.write("0")
    except Exception as e:
        print(f"Erro ao apagar o LED {led_path}: {e}")


# Função para piscar um único dígito no LED vermelho e separar com o LED verde
def blink_digit(digit):
    print(f"Piscando dígito: {digit}")
    for _ in range(int(digit)):
        set_led(LED_RED, 1, 0.4)  # Pisca devagar no vermelho
        time.sleep(0.4)  # Pausa entre piscadas
    set_led(LED_GREEN, 1, 0.6)  # Pisca o LED verde entre os dígitos
    time.sleep(0.6)  # Pequena pausa entre os dígitos


# Função principal para piscar o IP
def blink_ip(ip):
    print(f"Piscando IP: {ip}")

    # Pisca o LED verde 3 vezes no início do ciclo para indicar que um novo IP será mostrado
    for _ in range(3):
        set_led(LED_GREEN, 1, 0.5)
        time.sleep(0.5)

    time.sleep(2)  # Pausa antes de exibir o IP

    octets = ip.split(".")  # Separa os octetos do IP
    for i, octet in enumerate(octets):
        for digit in octet:
            blink_digit(digit)  # Pisca cada dígito individualmente

        if i < len(octets) - 1:
            print("Piscando LED verde para separar octetos")
            set_led(LED_GREEN, 1, 1.5)  # Pisca o LED verde para separação
            time.sleep(1)  # Pausa adicional

    print("Ciclo completo. Aguardando para repetir...\n")
    time.sleep(5)  # Aguarda antes de repetir


try:
    while True:
        ip = get_local_ip()
        blink_ip(ip)

except KeyboardInterrupt:
    print("\nBlink interrompido.")
