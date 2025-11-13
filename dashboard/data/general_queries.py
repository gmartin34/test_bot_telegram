from dashboard.utils.db_utils import execute_query_df, execute_scalar
import pandas as pd
from datetime import datetime


def get_actividad_mensual_anual():
    """
    Obtiene la actividad mensual para el año actual
    Retorna un DataFrame con los 12 meses del año
    """
    año_actual = datetime.now().year
    
    query = """
    SELECT 
        m.mes,
        COALESCE(COUNT(DISTINCT student_question.id_student), 0) as estudiantes_activos,
        COALESCE(COUNT(student_question.id), 0) as preguntas_respondidas,
        COALESCE(SUM(student_question.num_attempts), 0) as total_intentos
    FROM (
        SELECT 1 as mes UNION SELECT 2 UNION SELECT 3 UNION 
        SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION 
        SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION 
        SELECT 10 UNION SELECT 11 UNION SELECT 12
    ) m
    LEFT JOIN student_question ON 
        MONTH(student_question.last_attempt_date) = m.mes 
        AND YEAR(student_question.last_attempt_date) = %s
    GROUP BY m.mes
    ORDER BY m.mes
    """
    
    df = execute_query_df(query, (año_actual,))
    
    # Nombres de meses
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    df['mes_nombre'] = df['mes'].map(meses)
    
    return df


def get_resumen_general():

    """
    Obtiene un resumen general de estadísticas del sistema
    """
    query = """
    SELECT 
        (SELECT COUNT(*) FROM students) as total_estudiantes,
        (SELECT COUNT(*) FROM questions) as total_preguntas,
        (SELECT COUNT(*) FROM subject WHERE status = 'A') as asignaturas_activas,
        (SELECT COUNT(DISTINCT id_student) FROM student_question) as estudiantes_activos,
        (SELECT COUNT(DISTINCT id_student) 
         FROM student_question 
         WHERE last_attempt_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)) as activos_ultima_semana,
        (SELECT COUNT(DISTINCT id_student) 
         FROM student_question 
         WHERE last_attempt_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)) as activos_ultimo_mes
    """
    
    result = execute_query_df(query)
    
    if not result.empty:
        return result.iloc[0].to_dict()
    
    return {
        'total_estudiantes': 0,
        'total_preguntas': 0,
        'asignaturas_activas': 0,
        'estudiantes_activos': 0,
        'activos_ultima_semana': 0,
        'activos_ultimo_mes': 0
    }


def get_top_asignaturas():
    """
    Obtiene las top 5 asignaturas con más actividad
    """
    
    query = """
    SELECT 
        s.name as asignatura,
        COUNT(DISTINCT student_question.id_student) as estudiantes,
        COUNT(student_question.id) as preguntas_respondidas,
        AVG(CASE WHEN student_question.first_attempt = 1 THEN 100.0 ELSE 0 END) as porcentaje_acierto_primer_intento
    FROM subject s
    JOIN questions q ON s.id = q.id_subject
    LEFT JOIN student_question ON q.id = student_question.id_question
    WHERE s.status = 'A'
    GROUP BY s.id, s.name
    ORDER BY preguntas_respondidas DESC
    LIMIT 5
    """
    
    return execute_query_df(query)


def get_evolucion_diaria_ultima_semana():
    """
    Obtiene la evolución diaria de actividad en la última semana
    """
    query = """
    SELECT 
        DATE(last_attempt_date) as fecha,
        COUNT(DISTINCT id_student) as estudiantes_activos,
        COUNT(*) as preguntas_respondidas,
        SUM(num_attempts) as intentos_totales
    FROM student_question
    WHERE last_attempt_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    GROUP BY DATE(last_attempt_date)
    ORDER BY fecha DESC
    """
    
    df = execute_query_df(query)
    
    if not df.empty:
        # Formatear fecha para mejor visualización
        df['fecha_formato'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m')
        df['dia_semana'] = pd.to_datetime(df['fecha']).dt.day_name()
    
    return df