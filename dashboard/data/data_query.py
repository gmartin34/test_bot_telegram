from config import *
from dashboard.utils.db_utils import execute_query, execute_query_df, execute_scalar
import pandas as pd


def get_total_estudiantes():
    """Obtiene el número total de estudiantes"""
    query = "SELECT COUNT(*) FROM students"
    return execute_scalar(query) or 0


def get_total_preguntas():
    """Obtiene el número total de preguntas"""
    query = "SELECT COUNT(*) FROM questions"
    return execute_scalar(query) or 0


def get_estadisticas_intentos():
    """Obtiene estadísticas de intentos y aciertos"""
    query = """
    SELECT 
        COALESCE(SUM(num_attempts), 0) as total_intentos,
        COALESCE(SUM(mistake_number), 0) as total_fallos,
        COUNT(*) as total_registros,
        COALESCE(SUM(CASE WHEN first_attempt = 1 THEN 1 ELSE 0 END), 0) as aciertos_primer_intento,
        COALESCE( SUM(CASE  WHEN num_attempts >= 2 AND second_attempt = 1 THEN 1 ELSE 0 END), 0) as aciertos_segundo_intento,
        COALESCE( SUM(CASE  WHEN num_attempts >= 2 THEN 1 ELSE 0 END), 0) as total_segundo_intento
    FROM student_question
    """
    result = execute_query(query)
    
    if result and result[0]:
        total_intentos = result[0][0]
        total_fallos = result[0][1]
        total_registros = result[0][2]
        aciertos_primer = result[0][3]
        aciertos_segundo = result[0][4]
        total_segundo_intento = result[0][5]
        
        # Cálculo correcto de porcentajes
        porcentaje_acierto = ((total_intentos - total_fallos) / total_intentos * 100) if total_intentos > 0 else 0
        porcentaje_primer_intento = (aciertos_primer / total_registros * 100) if total_registros > 0 else 0
        porcentaje_segundo_intento = (aciertos_segundo / total_segundo_intento * 100) if total_registros > 0 else 0
        
        return {
            "total_intentos": total_intentos,
            "total_fallos": total_fallos,
            "total_registros": total_registros,
            "aciertos_primer_intento": aciertos_primer,
            "total_segundo_intento": total_segundo_intento,
            "porcentaje_acierto": round(porcentaje_acierto, 2),
            "porcentaje_primer_intento": round(porcentaje_primer_intento, 2),
            "porcentaje_segundo_intento": round(porcentaje_segundo_intento, 2)
        }
    
    return {
        "total_intentos": 0,
        "total_fallos": 0,
        "total_registros": 0,
        "aciertos_primer_intento": 0,
        "total_segundo_intento": 0,
        "porcentaje_acierto": 0,
        "porcentaje_primer_intento": 0,
        "porcentaje_segundo_intento": 0
    }


def get_progreso_estudiantes():
    """Obtiene el progreso de los estudiantes"""
    total_preguntas = get_total_preguntas()
    total_estudiantes = get_total_estudiantes()
    
    # Consulta optimizada para obtener el progreso
    query = """
    SELECT 
        COUNT(DISTINCT id_student) as estudiantes_con_actividad,
        SUM(CASE WHEN conteo.preguntas_respondidas = %s THEN 1 ELSE 0 END) as completado,
        SUM(CASE WHEN conteo.preguntas_respondidas > 0 AND conteo.preguntas_respondidas < %s THEN 1 ELSE 0 END) as en_progreso
    FROM (
        SELECT id_student, COUNT(DISTINCT id_question) as preguntas_respondidas
        FROM student_question
        GROUP BY id_student
    ) as conteo
    RIGHT JOIN students s ON s.id = conteo.id_student
    """
    
    result = execute_query(query, (total_preguntas, total_preguntas))
    
    if result and result[0]:
        estudiantes_con_actividad = result[0][0] or 0
        completado = result[0][1] or 0
        en_progreso = result[0][2] or 0
        sin_empezar = total_estudiantes - estudiantes_con_actividad
        
        df = pd.DataFrame({
            'progreso': ['Completado', 'Sin empezar', 'En progreso'],
            'total_progreso': [completado, sin_empezar, en_progreso]
        })
        
        return df
    
    # DataFrame por defecto si no hay datos
    return pd.DataFrame({
        'progreso': ['Completado', 'Sin empezar', 'En progreso'],
        'total_progreso': [0, total_estudiantes, 0]
    })


def get_actividad_por_mes():
    """Obtiene la actividad de estudiantes por mes"""
    query = """
    SELECT 
        YEAR(last_attempt_date) as año,
        MONTH(last_attempt_date) as mes,
        COUNT(DISTINCT id_student) as estudiantes_activos,
        COUNT(*) as preguntas_respondidas,
        SUM(num_attempts) as total_intentos
    FROM student_question
    WHERE last_attempt_date IS NOT NULL
    GROUP BY YEAR(last_attempt_date), MONTH(last_attempt_date)
    ORDER BY año DESC, mes DESC
    """
    
    df = execute_query_df(query)
    
    if not df.empty:
        # Mapear números de mes a nombres
        meses = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        df['mes_nombre'] = df['mes'].map(meses)
        df['periodo'] = df.apply(lambda x: f"{x['mes_nombre']} {x['año']}", axis=1)
    
    return df


def progreso_estudiantes():
    """Función principal que retorna todos los datos necesarios para el dashboard general"""
    try:
        # Obtener datos básicos
        
        total_estudiantes = get_total_estudiantes()
        total_preguntas = get_total_preguntas()
        estadisticas = get_estadisticas_intentos()
        df_progreso = get_progreso_estudiantes()
        df_actividad_mensual = get_actividad_por_mes()
        
        # Construir diccionario de respuesta
        data = {
            "dataframe": df_progreso,
            "num_tot_pre": total_preguntas,
            "num_tot_est": total_estudiantes,
            "num_tot_attempts": estadisticas["total_intentos"],
            "por_acierto": estadisticas["porcentaje_acierto"],
            "num_first_attempt": estadisticas["total_registros"],
            "num_pri_bien_por": estadisticas["porcentaje_primer_intento"],
            "tot_second_attempt": estadisticas["total_segundo_intento"],
            "num_segun_bien_por": estadisticas["porcentaje_segundo_intento"],
            "df_actividad_mensual": df_actividad_mensual
        }
        
        return data
        
    except Exception as e:
        print(f"Error al obtener datos del progreso: {e}")
        # Retornar estructura con valores por defecto
        return {
            "dataframe": pd.DataFrame({'progreso': [], 'total_progreso': []}),
            "num_tot_pre": 0,
            "num_tot_est": 0,
            "num_tot_attempts": 0,
            "por_acierto": 0,
            "num_first_attempt": 0,
            "num_pri_bien_por": 0,
            "df_actividad_mensual": pd.DataFrame()
        }