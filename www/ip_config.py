import subprocess
import io
import mariadb
from flask import Flask, render_template, request, send_file, redirect, url_for

app = Flask(__name__)

# Configuração do banco de dados
db_host = "127.0.0.1"
db_user = "root"
db_pass = "SINAPSE0109"
db_name = "Termometria"

# Caminho para o arquivo de configuração de rede
CONFIG_FILE = "/etc/systemd/network/10-end0.network"


def get_db_connection():
    try:
        conn = mariadb.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name
        )
        return conn
    except mariadb.Error as e:
        print(f"Erro ao conectar ao MariaDB: {e}")
        return None


def get_primary_key(cursor, table):
    """
    Obtém o nome da chave primária da tabela.
    """
    cursor.execute(f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'")
    result = cursor.fetchone()
    return result[4] if result else None


def get_current_ips():
    """
    Retorna uma lista com os IPs atuais da máquina utilizando o comando 'hostname -I'.
    """
    try:
        ips_raw = subprocess.check_output(["hostname", "-I"]).decode("utf-8").strip()
        return ips_raw.split()
    except Exception as e:
        return [f"Erro ao obter IPs atuais: {str(e)}"]


def get_current_hostname():
    """
    Retorna o hostname atual da máquina.
    """
    try:
        hostname = subprocess.check_output(["hostname"]).decode("utf-8").strip()
        return hostname
    except Exception as e:
        return f"Erro ao obter hostname: {str(e)}"


def clear_database():
    """
    Remove todos os registros das tabelas especificadas, mantendo apenas o último inserido.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return "Erro ao conectar ao banco de dados"

        cursor = conn.cursor()

        tables = [
            "failed_jobs",
            "receita_aeracao",
            "RegistroTemperaturas",
            "registro_instalacao",
            "arquivos",
            "registros",
"uploads"
        ]

        for table in tables:
            primary_key = get_primary_key(cursor, table)
            if primary_key:
                cursor.execute(
                    f"DELETE FROM {table} WHERE {primary_key} NOT IN (SELECT {primary_key} FROM (SELECT {primary_key} FROM {table} ORDER BY {primary_key} DESC LIMIT 1) AS t)")
                conn.commit()

        cursor.close()
        conn.close()
        return "Limpeza concluída com sucesso!"
    except mariadb.Error as e:
        return f"Erro ao limpar banco de dados: {str(e)}"


@app.route('/', methods=['GET', 'POST'])
def config_page():
    message = ""
    if request.method == 'POST':
        new_ip = request.form.get('ip')
        new_gateway = request.form.get('gateway')
        new_dns = request.form.get('dns')
        new_hostname = request.form.get('hostname')

        net_message = ""
        host_message = ""

        new_config = f"""
[Match]
Name=end0

[Network]
DHCP=yes
Address={new_ip}
Gateway={new_gateway}
DNS={new_dns}
"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                f.write(new_config)
            subprocess.run(["sudo", "systemctl", "restart", "systemd-networkd"], check=True)
            net_message = "Configuração de rede salva com sucesso! "
        except Exception as e:
            net_message = f"Erro ao salvar configuração de rede: {str(e)}. "

        try:
            subprocess.run(["sudo", "hostnamectl", "set-hostname", new_hostname], check=True)
            host_message = "Hostname alterado com sucesso! "
        except Exception as e:
            host_message = f"Erro ao alterar hostname: {str(e)}. "

        message = net_message + host_message

    current_ips = get_current_ips()
    current_hostname = get_current_hostname()

    return render_template("config.html", message=message, current_ips=current_ips, current_hostname=current_hostname)


@app.route('/clear', methods=['GET', 'POST'])
def clear_page():
    message = ""
    if request.method == 'POST':
        message = clear_database()

    return render_template("clear.html", message=message)


@app.route('/export', methods=['GET'])
def export_page():
    return render_template("export.html")


@app.route('/download-db', methods=['POST'])
def download_db():
    try:
        command = [
            "mysqldump",
            "-h", "127.0.0.1",
            "-u", db_user,
            f"--password={db_pass}",
            db_name
        ]
        dump = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        error_message = e.output.decode()
        return f"Erro ao exportar banco de dados: {error_message}", 500

    dump_file = io.BytesIO(dump)
    dump_file.seek(0)
    return send_file(
        dump_file,
        as_attachment=True,
        download_name=f"{db_name}_backup.sql",
        mimetype='application/sql'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
