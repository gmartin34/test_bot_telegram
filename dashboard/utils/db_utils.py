from contextlib import contextmanager
from database.db_connection import db_connection
import pandas as pd


@contextmanager
def get_db_cursor():
    """
    Context manager para manejar conexiones y cursores de base de datos.
    Asegura que las conexiones se cierren correctamente.
    """
    db = None
    cursor = None
    try:
        db = db_connection()
        cursor = db.cursor()
        yield cursor
    except Exception as e:
        print(f"Error en la conexión a la base de datos: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


def execute_query(query, params=None):
    """
    Ejecuta una consulta y retorna los resultados como lista de tuplas.
    
    Args:
        query (str): Consulta SQL a ejecutar
        params (tuple): Parámetros para la consulta (opcional)
    
    Returns:
        list: Lista de tuplas con los resultados
    """
    with get_db_cursor() as cursor:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()


def execute_query_df(query, params=None):
    """
    Ejecuta una consulta y retorna los resultados como DataFrame de pandas.
    
    Args:
        query (str): Consulta SQL a ejecutar
        params (tuple): Parámetros para la consulta (opcional)
    
    Returns:
        pd.DataFrame: DataFrame con los resultados
    """
    with get_db_cursor() as cursor:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Obtener nombres de columnas
        columns = [desc[0] for desc in cursor.description]
        
        # Obtener datos y crear DataFrame
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)


def execute_scalar(query, params=None):
    """
    Ejecuta una consulta que retorna un único valor.
    
    Args:
        query (str): Consulta SQL a ejecutar
        params (tuple): Parámetros para la consulta (opcional)
    
    Returns:
        any: El valor único retornado por la consulta
    """
    with get_db_cursor() as cursor:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None


def execute_many(query, data):
    """
    Ejecuta una consulta múltiples veces con diferentes datos.
    
    Args:
        query (str): Consulta SQL a ejecutar
        data (list): Lista de tuplas con los datos
    
    Returns:
        int: Número de filas afectadas
    """
    with get_db_cursor() as cursor:
        cursor.executemany(query, data)
        return cursor.rowcount