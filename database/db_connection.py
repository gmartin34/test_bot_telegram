import mysql.connector
from config import * # importamos variable de entorno o configuraciones


def db_connection():
# Conexión a la base de datos
    db = mysql.connector.connect(
        host=HOST,
        user=USER,      # Cambia esto si usas otro usuario
        password=PASSWORD,
        database=DATABASE
    )
    # Verificar la conexión
    if db.is_connected():
        print("Conexión a la base de datos exitosa")
    else:
        print("Error al conectar a la base de datos")
        return -1  # Retorna error si no se puede conectar       
    return db
  