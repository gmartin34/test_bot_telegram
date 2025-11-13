from dashboard.utils.db_utils import execute_query_df, execute_scalar
from dashboard.utils.date_utils import get_month_date_range, get_days_in_month
import pandas as pd
from datetime import datetime


def get_actividad_por_periodo(mes, año):
    """
    Obtiene las estadísticas de actividad para un período específico
    
    Args:
        mes: Número del mes (1-12)
        año: Año
    
    Returns:
        dict con las estadísticas del período
    """
    fecha_inicio, fecha_fin = get_month_date_range(mes, año)
    
    # Total de participantes registrados hasta el final del período
    query_participantes = """
    SELECT COUNT(*) 
    FROM students 
    WHERE id <= (
        SELECT MAX(id) FROM students 
        WHERE id IN (
            SELECT DISTINCT id_student 
            FROM student_question 
            WHERE first_attempt_date <= %s
        )
    )
    """
    total_participantes = execute_scalar(query_participantes, (fecha_fin,)) or 0
    
    # Total de preguntas disponibles
    total_preguntas = execute_scalar("SELECT COUNT(*) FROM questions WHERE state = 'A'") or 0
    
    # Días del período
    dias_periodo = get_days_in_month(mes, año)
    
    # Preguntas esperadas (suponiendo 1 pregunta por día por participante como ideal)
    preguntas_esperadas = min(total_participantes * dias_periodo, total_participantes * total_preguntas)
    
    # Preguntas respondidas en el período
    query_respondidas = """
    SELECT COUNT(*) 
    FROM student_question 
    WHERE last_attempt_date BETWEEN %s AND %s
    """
    preguntas_respondidas = execute_scalar(query_respondidas, (fecha_inicio, fecha_fin)) or 0
    
    # Indicador global de actividad
    indicador_actividad = (preguntas_respondidas / preguntas_esperadas * 100) if preguntas_esperadas > 0 else 0
    
    return {
        'mes': mes,
        'año': año,
        'total_participantes': total_participantes,
        'total_preguntas': total_preguntas,
        'dias_periodo': dias_periodo,
        'preguntas_esperadas': preguntas_esperadas,
        'preguntas_respondidas': preguntas_respondidas,
        'indicador_actividad': round(indicador_actividad, 2)
    }


def get_distribucion_actividad_periodo(mes, año):
    """
    Obtiene la distribución de participantes por nivel de actividad en un período
    """
    fecha_inicio, fecha_fin = get_month_date_range(mes, año)
    
    # Total de preguntas disponibles
    total_preguntas = execute_scalar("SELECT COUNT(*) FROM questions WHERE state = 'A'") or 0
    
    # Días del período
    dias_periodo = get_days_in_month(mes, año)
    
    # Preguntas esperadas por participante en el período
    preguntas_esperadas_por_participante = min(dias_periodo, total_preguntas)
    
    # Consulta para obtener actividad por participante
    query = """
    SELECT 
        s.id,
        s.name,
        COALESCE(act.preguntas_periodo, 0) as preguntas_periodo,
        COALESCE(act.dias_activo, 0) as dias_activo
    FROM students s
    LEFT JOIN (
        SELECT 
            id_student,
            COUNT(DISTINCT id_question) as preguntas_periodo,
            COUNT(DISTINCT DATE(last_attempt_date)) as dias_activo
        FROM student_question
        WHERE last_attempt_date BETWEEN %s AND %s
        GROUP BY id_student
    ) act ON s.id = act.id_student
    WHERE s.id IN (
        SELECT DISTINCT id_student 
        FROM student_question 
        WHERE first_attempt_date <= %s
    )
    """
    
    df = execute_query_df(query, (fecha_inicio, fecha_fin, fecha_fin))
    
    if not df.empty:
        # Calcular porcentaje de actividad para cada participante
        df['porcentaje_actividad'] = (df['preguntas_periodo'] / preguntas_esperadas_por_participante * 100).round(2)
        
        # Clasificar nivel de actividad
        df['nivel_actividad'] = df['porcentaje_actividad'].apply(clasificar_nivel_actividad)
        
        # Crear resumen
        resumen = df['nivel_actividad'].value_counts().reset_index()
        resumen.columns = ['nivel', 'cantidad']
        
        # Asegurar que todos los niveles estén presentes
        niveles = ['Muy activo', 'Activo', 'Poco activo', 'Inactivo']
        for nivel in niveles:
            if nivel not in resumen['nivel'].values:
                resumen = pd.concat([
                    resumen,
                    pd.DataFrame({'nivel': [nivel], 'cantidad': [0]})
                ], ignore_index=True)
        
        # Calcular porcentajes
        total = resumen['cantidad'].sum()
        resumen['porcentaje'] = (resumen['cantidad'] / total * 100).round(1) if total > 0 else 0
        
        # Ordenar por nivel
        orden = {'Muy activo': 0, 'Activo': 1, 'Poco activo': 2, 'Inactivo': 3}
        resumen['orden'] = resumen['nivel'].map(orden)
        resumen = resumen.sort_values('orden').drop('orden', axis=1)
        
        return resumen, df
    
    # DataFrame vacío si no hay datos
    return pd.DataFrame({
        'nivel': ['Muy activo', 'Activo', 'Poco activo', 'Inactivo'],
        'cantidad': [0, 0, 0, 0],
        'porcentaje': [0, 0, 0, 0]
    }), pd.DataFrame()


def clasificar_nivel_actividad(porcentaje):
    """Clasifica el nivel de actividad basado en el porcentaje"""
    if porcentaje >= 70:
        return 'Muy activo'
    elif porcentaje >= 50:
        return 'Activo'
    elif porcentaje > 0:
        return 'Poco activo'
    else:
        return 'Inactivo'


def get_evolucion_diaria_mes(mes, año):
    """
    Obtiene la evolución diaria de actividad para un mes específico
    """
    fecha_inicio, fecha_fin = get_month_date_range(mes, año)
    
    query = """
    SELECT 
        DATE(last_attempt_date) as fecha,
        COUNT(DISTINCT id_student) as participantes_activos,
        COUNT(DISTINCT id_question) as preguntas_diferentes,
        COUNT(*) as total_respuestas,
        SUM(CASE WHEN first_attempt = 1 THEN 1 ELSE 0 END) as aciertos_primer_intento
    FROM student_question
    WHERE DATE(last_attempt_date) BETWEEN %s AND %s
    GROUP BY DATE(last_attempt_date)
    ORDER BY fecha
    """
    
    df = execute_query_df(query, (fecha_inicio, fecha_fin))
    
    if not df.empty:
        # Calcular porcentaje de acierto diario
        df['porcentaje_acierto'] = (df['aciertos_primer_intento'] / df['total_respuestas'] * 100).round(1)
        
        # Formatear fecha
        df['dia'] = pd.to_datetime(df['fecha']).dt.day
        df['dia_semana'] = pd.to_datetime(df['fecha']).dt.day_name()
        
        # Crear DataFrame completo con todos los días del mes
        dias_mes = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
        df_completo = pd.DataFrame({'fecha': dias_mes})
        df_completo['dia'] = df_completo['fecha'].dt.day
        
        # Merge con datos reales
        df_final = df_completo.merge(df, on='dia', how='left', suffixes=('', '_y'))
        df_final.fillna(0, inplace=True)
        
        return df_final
    
    return pd.DataFrame()


def get_comparacion_meses(num_meses=6):
    """
    Obtiene comparación de actividad de los últimos n meses
    """
    query = """
    SELECT 
        YEAR(last_attempt_date) as año,
        MONTH(last_attempt_date) as mes,
        COUNT(DISTINCT id_student) as participantes_unicos,
        COUNT(*) as total_respuestas,
        SUM(CASE WHEN first_attempt = 1 THEN 1 ELSE 0 END) as aciertos,
        COUNT(DISTINCT DATE(last_attempt_date)) as dias_con_actividad
    FROM student_question
    WHERE last_attempt_date >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
        AND last_attempt_date <= CURDATE()
    GROUP BY YEAR(last_attempt_date), MONTH(last_attempt_date)
    ORDER BY año DESC, mes DESC
    LIMIT %s
    """
    
    df = execute_query_df(query, (num_meses, num_meses))
    
    if not df.empty:
        # Mapear nombres de meses
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        
        df['mes_nombre'] = df['mes'].map(meses)
        df['periodo'] = df.apply(lambda x: f"{x['mes_nombre']}-{str(x['año'])[-2:]}", axis=1)
        df['porcentaje_acierto'] = (df['aciertos'] / df['total_respuestas'] * 100).round(1)
        
        # Invertir orden para mostrar cronológicamente
        df = df.iloc[::-1]
    
    return df


def get_estadisticas_detalladas_periodo(mes, año):
    """
    Obtiene estadísticas detalladas para un período específico
    """
    fecha_inicio, fecha_fin = get_month_date_range(mes, año)
    query = """
    SELECT 
        -- Métricas generales
        COUNT(DISTINCT sq.id_student) as participantes_activos,
        COUNT(DISTINCT sq.id_question) as preguntas_unicas_respondidas,
        COUNT(*) as total_respuestas,
        AVG(sq.num_attempts) as promedio_intentos,
        
        -- Métricas de rendimiento
        SUM(CASE WHEN sq.first_attempt = 1 THEN 1 ELSE 0 END) as aciertos_primer_intento,
        SUM(CASE WHEN sq.second_attempt = 1 THEN 1 ELSE 0 END) as aciertos_segundo_intento,
        
        -- Métricas de participación
        COUNT(DISTINCT CASE 
            WHEN DATE(sq.last_attempt_date) = DATE(sq.first_attempt_date) 
            THEN sq.id_student 
        END) as nuevos_participantes,
        
        -- Distribución por asignatura
        COUNT(DISTINCT q.id_subject) as asignaturas_activas
        
    FROM student_question sq
    JOIN questions q ON sq.id_question = q.id
    WHERE sq.last_attempt_date BETWEEN %s AND %s
    """
    
    result = execute_query_df(query, (fecha_inicio, fecha_fin))
    
    if not result.empty and result.iloc[0]['total_respuestas'] > 0:
        row = result.iloc[0]
        return {
            'participantes_activos': int(row['participantes_activos']),
            'preguntas_unicas': int(row['preguntas_unicas_respondidas']),
            'total_respuestas': int(row['total_respuestas']),
            'promedio_intentos': round(row['promedio_intentos'], 2),
            'porcentaje_acierto_primero': round(row['aciertos_primer_intento'] / row['total_respuestas'] * 100, 1),
            'porcentaje_acierto_segundo': round(row['aciertos_segundo_intento'] / row['total_respuestas'] * 100, 1) if row['aciertos_segundo_intento'] else 0,
            'nuevos_participantes': int(row['nuevos_participantes']),
            'asignaturas_activas': int(row['asignaturas_activas'])
        }
    
    return {
        'participantes_activos': 0,
        'preguntas_unicas': 0,
        'total_respuestas': 0,
        'promedio_intentos': 0,
        'porcentaje_acierto_primero': 0,
        'porcentaje_acierto_segundo': 0,
        'nuevos_participantes': 0,
        'asignaturas_activas': 0
    }