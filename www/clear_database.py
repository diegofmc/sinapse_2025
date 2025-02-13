import mariadb

# Configuração do banco de dados
db_host = "127.0.0.1"
db_user = "root"
db_pass = "SINAPSE0109"
db_name = "Termometria"


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


def clear_database():
    """
    Remove todos os registros das tabelas especificadas, mantendo apenas o último inserido.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            print("Erro ao conectar ao banco de dados")
            return

        cursor = conn.cursor()

        tables = [
            "failed_jobs",
            "receita_aeracao",
            "RegistroTemperaturas",
            "registro_instalacao",
            "arquivos",
            "registros"
        ]

        for table in tables:
            primary_key = get_primary_key(cursor, table)
            if primary_key:
                cursor.execute(
                    f"DELETE FROM {table} WHERE {primary_key} NOT IN (SELECT {primary_key} FROM (SELECT {primary_key} FROM {table} ORDER BY {primary_key} DESC LIMIT 1) AS t)")
                conn.commit()

        cursor.close()
        conn.close()
        print("Limpeza concluída com sucesso!")
    except mariadb.Error as e:
        print(f"Erro ao limpar banco de dados: {str(e)}")


if __name__ == "__main__":
    print("Iniciando limpeza emergencial do banco de dados...")
    clear_database()
