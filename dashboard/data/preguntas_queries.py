from dashboard.utils.db_utils import execute_query_df, execute_scalar
import pandas as pd


def get_estadisticas_preguntas():
    """
    Obtiene estadísticas detalladas de cada pregunta
    """
    query = """
    SELECT 
        q.id as id_pregunta,
        q.question as pregunta,
        s.name as asignatura,
        q.level as nivel,
        COALESCE(stats.participantes_respondieron, 0) as participantes_respondieron,
        COALESCE(stats.total_intentos, 0) as total_intentos,
        COALESCE(stats.veces_retirada, 0) as veces_retirada,
        COALESCE(stats.aciertos_primer_intento, 0) as aciertos_primer_intento,
        COALESCE(stats.total_primer_intento, 0) as total_primer_intento,
        COALESCE(stats.aciertos_segundo_intento, 0) as aciertos_segundo_intento,
        COALESCE(stats.total_segundo_intento, 0) as total_segundo_intento
    FROM questions q
    LEFT JOIN subject s ON q.id_subject = s.id
    LEFT JOIN (
        SELECT 
            id_question,
            COUNT(DISTINCT id_student) as participantes_respondieron,
            SUM(num_attempts) as total_intentos,
            SUM(CASE WHEN num_attempts >= 2 AND mistake_number = 0 THEN 1 ELSE 0 END) as veces_retirada,
            SUM(CASE WHEN first_attempt = 1 THEN 1 ELSE 0 END) as aciertos_primer_intento,
            COUNT(CASE WHEN num_attempts >= 1 THEN 1 END) as total_primer_intento,
            SUM(CASE WHEN second_attempt = 1 THEN 1 ELSE 0 END) as aciertos_segundo_intento,
            COUNT(CASE WHEN num_attempts >= 2 THEN 1 END) as total_segundo_intento
        FROM student_question
        GROUP BY id_question
    ) stats ON q.id = stats.id_question
    WHERE q.state = 'A'
    ORDER BY q.id
    """
    
    df = execute_query_df(query)
    
    if not df.empty:
        # Calcular métricas derivadas
        df['media_intentos'] = df.apply(
            lambda x: round(x['total_intentos'] / x['participantes_respondieron'], 2) 
            if x['participantes_respondieron'] > 0 else 0, 
            axis=1
        )
        
        df['porcentaje_acierto_primero'] = df.apply(
            lambda x: round((x['aciertos_primer_intento'] / x['total_primer_intento']) * 100, 2) 
            if x['total_primer_intento'] > 0 else 0, 
            axis=1
        )
        
        df['porcentaje_acierto_segundo'] = df.apply(
            lambda x: round((x['aciertos_segundo_intento'] / x['total_segundo_intento']) * 100, 2) 
            if x['total_segundo_intento'] > 0 else 0, 
            axis=1
        )
        
        df['diferencia_porcentajes'] = df['porcentaje_acierto_segundo'] - df['porcentaje_acierto_primero']
        
        # Clasificar dificultad
        df['dificultad'] = df['porcentaje_acierto_primero'].apply(clasificar_dificultad)
    
    return df


def clasificar_dificultad(porcentaje_acierto):
    """Clasifica la dificultad de una pregunta basándose en el porcentaje de acierto"""
    if porcentaje_acierto >= 70:
        return 'Fácil'
    elif porcentaje_acierto >= 40:
        return 'Media'
    else:
        return 'Difícil'


def get_resumen_preguntas():
    """
    Obtiene un resumen general de las preguntas
    """
    query = """
    SELECT 
        COUNT(DISTINCT q.id) as total_preguntas,
        COUNT(DISTINCT CASE WHEN stats.participantes > 0 THEN q.id END) as preguntas_respondidas,
        COUNT(DISTINCT CASE WHEN stats.participantes = 0 OR stats.participantes IS NULL THEN q.id END) as preguntas_sin_responder,
        AVG(CASE WHEN stats.porcentaje_primero IS NOT NULL THEN stats.porcentaje_primero ELSE NULL END) as promedio_acierto_primero,
        AVG(CASE WHEN stats.media_intentos IS NOT NULL THEN stats.media_intentos ELSE NULL END) as promedio_intentos
    FROM questions q
    LEFT JOIN (
        SELECT 
            id_question,
            COUNT(DISTINCT id_student) as participantes,
            AVG(num_attempts) as media_intentos,
            (SUM(CASE WHEN first_attempt = 1 THEN 1 ELSE 0 END) * 100.0 / 
             NULLIF(COUNT(CASE WHEN num_attempts >= 1 THEN 1 END), 0)) as porcentaje_primero
        FROM student_question
        GROUP BY id_question
    ) stats ON q.id = stats.id_question
    WHERE q.state = 'A'
    """
    
    result = execute_query_df(query)
    
    if not result.empty:
        return {
            'total_preguntas': int(result.iloc[0]['total_preguntas']),
            'preguntas_respondidas': int(result.iloc[0]['preguntas_respondidas']),
            'preguntas_sin_responder': int(result.iloc[0]['preguntas_sin_responder']),
            'promedio_acierto_primero': round(result.iloc[0]['promedio_acierto_primero'] or 0, 2),
            'promedio_intentos': round(result.iloc[0]['promedio_intentos'] or 0, 2)
        }
    
    return {
        'total_preguntas': 0,
        'preguntas_respondidas': 0,
        'preguntas_sin_responder': 0,
        'promedio_acierto_primero': 0,
        'promedio_intentos': 0
    }


def get_preguntas_por_asignatura():
    """
    Obtiene estadísticas agrupadas por asignatura
    """
    query = """
    SELECT 
        s.name as asignatura,
        COUNT(DISTINCT q.id) as total_preguntas,
        COUNT(DISTINCT sq.id_question) as preguntas_respondidas,
        AVG(CASE 
            WHEN sq.total_intentos > 0 
            THEN (sq.aciertos_primero * 100.0 / sq.total_primero)
            ELSE NULL 
        END) as promedio_acierto_primero,
        SUM(sq.total_intentos) as intentos_totales
    FROM subject s
    LEFT JOIN questions q ON s.id = q.id_subject AND q.state = 'A'
    LEFT JOIN (
        SELECT 
            q2.id_subject,
            sq2.id_question,
            SUM(sq2.num_attempts) as total_intentos,
            SUM(CASE WHEN sq2.first_attempt = 1 THEN 1 ELSE 0 END) as aciertos_primero,
            COUNT(CASE WHEN sq2.num_attempts >= 1 THEN 1 END) as total_primero
        FROM student_question sq2
        JOIN questions q2 ON sq2.id_question = q2.id
        GROUP BY q2.id_subject, sq2.id_question
    ) sq ON q.id = sq.id_question
    WHERE s.status = 'A'
    GROUP BY s.id, s.name
    HAVING COUNT(DISTINCT q.id) > 0
    ORDER BY total_preguntas DESC
    """
    
    return execute_query_df(query)


def get_top_preguntas_faciles_dificiles(limite=5):
    """
    Obtiene las preguntas más fáciles y más difíciles
    """
    # Preguntas más fáciles
    query_faciles = """
    SELECT 
        q.id,
        q.question as pregunta,
        s.name as asignatura,
        (SUM(CASE WHEN sq.first_attempt = 1 THEN 1 ELSE 0 END) * 100.0 / 
         NULLIF(COUNT(CASE WHEN sq.num_attempts >= 1 THEN 1 END), 0)) as porcentaje_acierto,
        COUNT(DISTINCT sq.id_student) as participantes
    FROM questions q
    JOIN subject s ON q.id_subject = s.id
    JOIN student_question sq ON q.id = sq.id_question
    WHERE q.state = 'A'
    GROUP BY q.id, q.question, s.name
    HAVING participantes >= 5  -- Solo preguntas con al menos 5 respuestas
    ORDER BY porcentaje_acierto DESC
    LIMIT %s
    """
    
    # Preguntas más difíciles
    query_dificiles = """
    SELECT 
        q.id,
        q.question as pregunta,
        s.name as asignatura,
        (SUM(CASE WHEN sq.first_attempt = 1 THEN 1 ELSE 0 END) * 100.0 / 
         NULLIF(COUNT(CASE WHEN sq.num_attempts >= 1 THEN 1 END), 0)) as porcentaje_acierto,
        COUNT(DISTINCT sq.id_student) as participantes
    FROM questions q
    JOIN subject s ON q.id_subject = s.id
    JOIN student_question sq ON q.id = sq.id_question
    WHERE q.state = 'A'
    GROUP BY q.id, q.question, s.name
    HAVING participantes >= 5  -- Solo preguntas con al menos 5 respuestas
    ORDER BY porcentaje_acierto ASC
    LIMIT %s
    """
    
    df_faciles = execute_query_df(query_faciles, (limite,))
    df_dificiles = execute_query_df(query_dificiles, (limite,))
    
    return {
        'faciles': df_faciles,
        'dificiles': df_dificiles
    }