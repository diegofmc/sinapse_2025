import mariadb

try:
    conn = mariadb.connect(
        user="leitor_termo",
        password="termometria",
        host="127.0.0.1",
        port=3306,
        database="Termometria"
    )
    print("Conectado ao banco de dados!")
    conn.close()
except mariadb.Error as e:
    print(f"Erro ao conectar: {e}")
