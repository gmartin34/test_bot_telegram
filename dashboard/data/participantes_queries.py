from dashboard.utils.db_utils import execute_query_df, execute_scalar
import pandas as pd
from datetime import datetime, timedelta


def get_datos_participantes():
    """
    Obtiene datos detallados de todos los participantes
    """
    # Primero obtenemos el total de preguntas
    total_preguntas = execute_scalar("SELECT COUNT(*) FROM questions WHERE state = 'A'")
    
    query = """
    SELECT 
        s.id,
        s.name as nombre,
        s.email,
        COALESCE(stats.preguntas_respondidas, 0) as preguntas_respondidas,
        COALESCE(stats.preguntas_retiradas, 0) as preguntas_retiradas,
        COALESCE(stats.total_intentos, 0) as total_intentos,
        COALESCE(stats.aciertos_primer_intento, 0) as aciertos_primer_intento,
        COALESCE(stats.total_primer_intento, 0) as total_primer_intento,
        COALESCE(stats.aciertos_segundo_intento, 0) as aciertos_segundo_intento,
        COALESCE(stats.total_segundo_intento, 0) as total_segundo_intento,
        stats.ultima_actividad,
        stats.primera_actividad,
        DATEDIFF(CURDATE(), stats.ultima_actividad) as dias_inactivo
    FROM students s
    LEFT JOIN (
        SELECT 
            id_student,
            COUNT(DISTINCT id_question) as preguntas_respondidas,
            COUNT(DISTINCT CASE WHEN (num_attempts - mistake_number >= 2) THEN id_question END) as preguntas_retiradas,
            SUM(num_attempts) as total_intentos,
            SUM(CASE WHEN first_attempt = 1 THEN 1 ELSE 0 END) as aciertos_primer_intento,
            COUNT(CASE WHEN num_attempts >= 1 THEN 1 END) as total_primer_intento,
            SUM(CASE WHEN second_attempt = 1 THEN 1 ELSE 0 END) as aciertos_segundo_intento,
            COUNT(CASE WHEN num_attempts >= 2 THEN 1 END) as total_segundo_intento,
            MAX(last_attempt_date) as ultima_actividad,
            MIN(first_attempt_date) as primera_actividad
        FROM student_question
        GROUP BY id_student
    ) stats ON s.id = stats.id_student
    ORDER BY s.name
    """
    
    df = execute_query_df(query)
    
    if not df.empty:
        # Calcular progreso
        df['progreso'] = df.apply(lambda row: calcular_progreso(
            row['preguntas_respondidas'], 
            total_preguntas, 
            row['dias_inactivo']
        ), axis=1)
        
        # Calcular nivel de actividad
        df['actividad'] = df.apply(lambda row: calcular_nivel_actividad(
            row['preguntas_respondidas'],
            total_preguntas,
            row['primera_actividad'],
            row['ultima_actividad']
        ), axis=1)
        
        # Calcular porcentajes de acierto
        df['porcentaje_primer_intento'] = df.apply(
            lambda x: round((x['aciertos_primer_intento'] / x['total_primer_intento']) * 100, 1) 
            if x['total_primer_intento'] > 0 else 0, 
            axis=1
        )
        
        df['porcentaje_segundo_intento'] = df.apply(
            lambda x: round((x['aciertos_segundo_intento'] / x['total_segundo_intento']) * 100, 1) 
            if x['total_segundo_intento'] > 0 else 0, 
            axis=1
        )
        
        df['diferencia_porcentajes'] = df['porcentaje_segundo_intento'] - df['porcentaje_primer_intento']
        
        # Porcentaje de preguntas completadas
        df['porcentaje_completado'] = (df['preguntas_respondidas'] / total_preguntas * 100).round(1)
        df['porcentaje_retiradas'] = (df['preguntas_retiradas'] / total_preguntas * 100).round(1)
        
        # Total de preguntas para el desempeño
        df['total_preguntas'] = total_preguntas
    
    return df


def calcular_progreso(preguntas_respondidas, total_preguntas, dias_inactivo):
    """
    Calcula el estado de progreso de un participante
    """
    if preguntas_respondidas == 0:
        return "No ha comenzado"
    elif preguntas_respondidas >= total_preguntas:
        return "Completado"
    elif dias_inactivo is not None and dias_inactivo > 7:
        return "Riesgo de abandono"
    else:
        return "Progresando"


def calcular_nivel_actividad(preguntas_respondidas, total_preguntas, primera_actividad, ultima_actividad):
    """
    Calcula el nivel de actividad de un participante
    """
    if preguntas_respondidas == 0:
        return "Inactivo"
    
    # Calcular días activos
    if primera_actividad and ultima_actividad:
        dias_activo = (ultima_actividad - primera_actividad).days + 1
        if dias_activo == 0:
            dias_activo = 1
            
        # Preguntas esperadas (asumiendo 1 pregunta por día como referencia)
        preguntas_esperadas = min(dias_activo, total_preguntas)
        
        # Ratio de actividad
        ratio_actividad = (preguntas_respondidas / preguntas_esperadas) * 100
        
        if ratio_actividad >= 70:
            return "Muy activo"
        elif ratio_actividad >= 50:
            return "Activo"
        elif ratio_actividad > 0:
            return "Poco activo"
    
    return "Poco activo"


def get_resumen_participantes():
    """
    Obtiene un resumen general de los participantes
    """
    query = """
    SELECT 
        COUNT(DISTINCT s.id) as total_participantes,
        COUNT(DISTINCT sq.id_student) as participantes_activos,
        COUNT(DISTINCT CASE 
            WHEN sq.id_student IS NULL THEN s.id 
        END) as sin_comenzar,
        COUNT(DISTINCT CASE 
            WHEN DATEDIFF(CURDATE(), sq.ultima_actividad) > 7 
            AND sq.preguntas_respondidas < (SELECT COUNT(*) FROM questions WHERE state = 'A')
            THEN sq.id_student 
        END) as riesgo_abandono,
        COUNT(DISTINCT CASE 
            WHEN sq.preguntas_respondidas >= (SELECT COUNT(*) FROM questions WHERE state = 'A') 
            THEN sq.id_student 
        END) as completado,
        AVG(sq.porcentaje_acierto_primero) as promedio_acierto_primero
    FROM students s
    LEFT JOIN (
        SELECT 
            id_student,
            COUNT(DISTINCT id_question) as preguntas_respondidas,
            MAX(last_attempt_date) as ultima_actividad,
            (SUM(CASE WHEN first_attempt = 1 THEN 1 ELSE 0 END) * 100.0 / 
             NULLIF(COUNT(CASE WHEN num_attempts >= 1 THEN 1 END), 0)) as porcentaje_acierto_primero
        FROM student_question
        GROUP BY id_student
    ) sq ON s.id = sq.id_student
    """
    
    result = execute_query_df(query)
    
    if not result.empty:
        return {
            'total_participantes': int(result.iloc[0]['total_participantes']),
            'participantes_activos': int(result.iloc[0]['participantes_activos']),
            'sin_comenzar': int(result.iloc[0]['sin_comenzar']),
            'riesgo_abandono': int(result.iloc[0]['riesgo_abandono'] or 0),
            'completado': int(result.iloc[0]['completado'] or 0),
            'promedio_acierto': round(result.iloc[0]['promedio_acierto_primero'] or 0, 1)
        }
    
    return {
        'total_participantes': 0,
        'participantes_activos': 0,
        'sin_comenzar': 0,
        'riesgo_abandono': 0,
        'completado': 0,
        'promedio_acierto': 0
    }


def get_distribucion_actividad():
    """
    Obtiene la distribución de participantes por nivel de actividad
    """
    df_participantes = get_datos_participantes()
    
    if not df_participantes.empty:
        # Contar por nivel de actividad
        distribucion = df_participantes['actividad'].value_counts().reset_index()
        distribucion.columns = ['actividad', 'cantidad']
        
        # Asegurar que todos los niveles estén presentes
        niveles = ['Muy activo', 'Activo', 'Poco activo', 'Inactivo']
        for nivel in niveles:
            if nivel not in distribucion['actividad'].values:
                distribucion = pd.concat([
                    distribucion,
                    pd.DataFrame({'actividad': [nivel], 'cantidad': [0]})
                ], ignore_index=True)
        
        # Calcular porcentajes
        total = distribucion['cantidad'].sum()
        distribucion['porcentaje'] = (distribucion['cantidad'] / total * 100).round(1)
        
        return distribucion
    
    return pd.DataFrame({
        'actividad': ['Muy activo', 'Activo', 'Poco activo', 'Inactivo'],
        'cantidad': [0, 0, 0, 0],
        'porcentaje': [0, 0, 0, 0]
    })


def get_top_participantes(limite=10):
    """
    Obtiene los top participantes por diferentes métricas
    """
    # Top por preguntas completadas
    query_completadas = """
    SELECT 
        s.name,
        COUNT(DISTINCT sq.id_question) as preguntas_respondidas,
        (COUNT(DISTINCT sq.id_question) * 100.0 / 
         (SELECT COUNT(*) FROM questions WHERE state = 'A')) as porcentaje_completado
    FROM students s
    JOIN student_question sq ON s.id = sq.id_student
    GROUP BY s.id, s.name
    ORDER BY preguntas_respondidas DESC
    LIMIT %s
    """
    
    # Top por porcentaje de acierto
    query_acierto = """
    SELECT 
        s.name,
        COUNT(sq.id) as total_respuestas,
        (SUM(CASE WHEN sq.first_attempt = 1 THEN 1 ELSE 0 END) * 100.0 / 
         NULLIF(COUNT(CASE WHEN sq.num_attempts >= 1 THEN 1 END), 0)) as porcentaje_acierto
    FROM students s
    JOIN student_question sq ON s.id = sq.id_student
    GROUP BY s.id, s.name
    HAVING COUNT(sq.id) >= 10  -- Al menos 10 respuestas
    ORDER BY porcentaje_acierto DESC
    LIMIT %s
    """
    
    df_completadas = execute_query_df(query_completadas, (limite,))
    df_acierto = execute_query_df(query_acierto, (limite,))
    
    return {
        'por_completadas': df_completadas,
        'por_acierto': df_acierto
    }