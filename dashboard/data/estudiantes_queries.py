from dashboard.utils.db_utils import execute_query_df, execute_query, get_db_cursor
import pandas as pd
from datetime import datetime


def get_estudiantes_pendientes():
    """
    Obtiene todos los estudiantes con estado pendiente
    """
    query = """
    SELECT DISTINCT
        s.id,
        s.cid,
        s.name,
        s.email,
        MIN(ss.id) as fecha_registro
    FROM students s
    INNER JOIN student_subject ss ON s.id = ss.id_student
    WHERE ss.state = 'P'
    GROUP BY s.id, s.cid, s.name, s.email
    ORDER BY MIN(ss.id) DESC
    """
    
    df = execute_query_df(query)
    
    # Simular fecha de registro basada en el ID (temporal)
    if not df.empty:
    #    df['fecha_registro'] = pd.to_datetime('2024-01-01') + pd.to_timedelta(df['fecha_registro'], unit='D')
         df['fecha_registro'] = pd.to_datetime(datetime.now().date()) + pd.to_timedelta(df['fecha_registro'], unit='D') 
    return df


def get_estudiantes_activos():
    """
    Obtiene todos los estudiantes activos o dados de baja con sus estadísticas
    """
    query = """
    SELECT 
        s.id,
        s.cid,
        s.name,
        s.email,
        ss.state,
        COUNT(DISTINCT sq.id_question) as preguntas_respondidas,
        CASE 
            WHEN COUNT(sq.id) > 0 
            THEN (SUM(CASE WHEN sq.first_attempt = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(sq.id))
            ELSE 0 
        END as porcentaje_acierto,
        MAX(sq.last_attempt_date) as ultima_actividad
    FROM students s
    INNER JOIN student_subject ss ON s.id = ss.id_student
    LEFT JOIN student_question sq ON s.id = sq.id_student
    WHERE ss.state IN ('A', 'B')
    GROUP BY s.id, s.cid, s.name, s.email, ss.state
    ORDER BY s.name
    """
    
    return execute_query_df(query)


def aprobar_estudiante(student_id):
    """
    Aprueba un estudiante cambiando su estado de 'P' a 'A'
    """
    with get_db_cursor() as cursor:
        try:
            query = """
            UPDATE student_subject 
            SET state = 'A' 
            WHERE id_student = %s AND state = 'P'
            """
            cursor.execute(query, (student_id,))
            cursor._connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al aprobar estudiante: {e}")
            cursor._connection.rollback()
            return False


def cambiar_estado_estudiante(student_id, nuevo_estado):
    """
    Cambia el estado de un estudiante (A o B)
    """
    with get_db_cursor() as cursor:
        try:
            query = """
            UPDATE student_subject 
            SET state = %s 
            WHERE id_student = %s
            """
            cursor.execute(query, (nuevo_estado, student_id))
            cursor._connection.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al cambiar estado del estudiante: {e}")
            cursor._connection.rollback()
            return False


def get_estadisticas_estudiantes():
    """
    Obtiene estadísticas generales de estudiantes
    """
    query = """
    SELECT 
        COUNT(DISTINCT CASE WHEN ss.state = 'A' THEN s.id END) as activos,
        COUNT(DISTINCT CASE WHEN ss.state = 'P' THEN s.id END) as pendientes,
        COUNT(DISTINCT CASE WHEN ss.state = 'B' THEN s.id END) as baja,
        COUNT(DISTINCT s.id) as total
    FROM students s
    LEFT JOIN student_subject ss ON s.id = ss.id_student
    """
    
    result = execute_query_df(query)
    
    if not result.empty:
        return result.iloc[0].to_dict()
    
    return {
        'activos': 0,
        'pendientes': 0,
        'baja': 0,
        'total': 0
    }


def get_historial_estudiante(student_id):
    """
    Obtiene el historial completo de un estudiante
    """
    query = """
    SELECT 
        s.id,
        s.name,
        s.email,
        ss.state,
        COUNT(DISTINCT sq.id_question) as preguntas_respondidas,
        SUM(sq.num_attempts) as total_intentos,
        SUM(CASE WHEN sq.first_attempt = 1 THEN 1 ELSE 0 END) as aciertos_primero,
        SUM(CASE WHEN sq.second_attempt = 1 THEN 1 ELSE 0 END) as aciertos_segundo,
        MIN(sq.first_attempt_date) as primera_actividad,
        MAX(sq.last_attempt_date) as ultima_actividad
    FROM students s
    LEFT JOIN student_subject ss ON s.id = ss.id_student
    LEFT JOIN student_question sq ON s.id = sq.id_student
    WHERE s.id = %s
    GROUP BY s.id, s.name, s.email, ss.state
    """
    
    return execute_query_df(query, (student_id,))