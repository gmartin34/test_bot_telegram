from dashboard.utils.db_utils import execute_query_df, execute_scalar, execute_query, get_db_cursor
import pandas as pd


def get_all_subjects():
    """Obtiene todas las asignaturas con sus datos"""
    query = """
    SELECT 
        s.id,
        s.name,
        s.faculty,
        s.num_success,
        s.status,
        COUNT(q.id) as total_questions
    FROM subject s
    LEFT JOIN questions q ON s.id = q.id_subject
    GROUP BY s.id, s.name, s.faculty, s.num_success, s.status
    ORDER BY s.faculty, s.name
    """
    return execute_query_df(query)


def get_questions_by_subject(subject_id):
    """Obtiene las preguntas de una asignatura específica con estadísticas"""
    query = """
    SELECT 
        q.id,
        q.id_subject,
        q.state,
        q.level,
        q.question,
        q.solution,
        q.why,
        q.answer1,

        q.answer2,
        q.answer3,
        q.answer4,
        s.name as subject_name,
        COALESCE(stats.participantes, 0) as participantes,
        COALESCE(stats.total_intentos, 0) as total_intentos,
        COALESCE(stats.media_intentos, 0) as media_intentos
    FROM questions q
    JOIN subject s ON q.id_subject = s.id
    LEFT JOIN (
        SELECT 
            id_question,
            COUNT(DISTINCT id_student) as participantes,
            SUM(num_attempts) as total_intentos,
            AVG(num_attempts) as media_intentos
        FROM student_question
        GROUP BY id_question
    ) stats ON q.id = stats.id_question
    WHERE q.id_subject = %s
    ORDER BY q.id
    """
    return execute_query_df(query, (subject_id,))


def update_subject_status(subject_id, status):
    """Actualiza el estado de una asignatura"""
    with get_db_cursor() as cursor:
        query = "UPDATE subject SET status = %s WHERE id = %s"
        cursor.execute(query, (status, subject_id))
        cursor._connection.commit()
        return cursor.rowcount > 0


def create_question(data):
    """Crea una nueva pregunta"""
    with get_db_cursor() as cursor:
        # Obtener el próximo ID disponible para la asignatura
        query_max_id = """
        SELECT COALESCE(MAX(id), 0) + 1 
        FROM questions 
        WHERE id_subject = %s
        """
        cursor.execute(query_max_id, (data['id_subject'],))
        next_id = cursor.fetchone()[0]
        
        query = """
        INSERT INTO questions 
        (id, id_subject, state, level, question, solution, why, answer1, answer2, answer3, answer4)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            next_id,
            data['id_subject'],
            data.get('state', 'A'),
            data.get('level', 1),
            data['question'],
            data['solution'],
            data.get('why', ''),
            data['answer1'],
            data['answer2'],
            data['answer3'],
            data['answer4']
        )
        cursor.execute(query, params)
        cursor._connection.commit()
        return cursor.rowcount > 0


def update_question(question_id, subject_id, data):
    """Actualiza una pregunta existente"""
    with get_db_cursor() as cursor:
        query = """
        UPDATE questions 
        SET state = %s, level = %s, question = %s, solution = %s, 
            why = %s, answer1 = %s, answer2 = %s, answer3 = %s, answer4 = %s
        WHERE id = %s AND id_subject = %s
        """
        params = (
            data.get('state', 'A'),
            data.get('level', 1),
            data['question'],
            data['solution'],
            data.get('why', ''),
            data['answer1'],
            data['answer2'],
            data['answer3'],
            data['answer4'],
            question_id,
            subject_id
        )
        cursor.execute(query, params)
        cursor._connection.commit()
        return cursor.rowcount > 0


def delete_question(question_id, subject_id):
    """Elimina una pregunta"""
    with get_db_cursor() as cursor:
        # Primero verificar si hay respuestas asociadas
        check_query = """
        SELECT COUNT(*) 
        FROM student_question 
        WHERE id_question = %s
        """
        cursor.execute(check_query, (question_id,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Si hay respuestas, solo desactivar
            query = "UPDATE questions SET state = 'I' WHERE id = %s AND id_subject = %s"
            cursor.execute(query, (question_id, subject_id))
        else:
            # Si no hay respuestas, eliminar
            query = "DELETE FROM questions WHERE id = %s AND id_subject = %s"
            cursor.execute(query, (question_id, subject_id))
        
        cursor._connection.commit()
        return cursor.rowcount > 0, count > 0


def get_question_details(question_id, subject_id):
    """Obtiene los detalles de una pregunta específica"""
    query = """
    SELECT * FROM questions 
    WHERE id = %s AND id_subject = %s
    """
    df = execute_query_df(query, (question_id, subject_id))
    return df.to_dict('records')[0] if not df.empty else None

def delete_question(question_id):
    """Elimina una pregunta por su ID. Si tiene respuestas asociadas, solo la desactiva."""
    with get_db_cursor() as cursor:
        # Buscar el id_subject de la pregunta
        cursor.execute("SELECT id_subject FROM questions WHERE id = %s", (question_id,))
        result = cursor.fetchone()
        if not result:
            return False  # No existe la pregunta

        subject_id = result[0]

        # Verificar si hay respuestas asociadas
        check_query = "SELECT COUNT(*) FROM student_question WHERE id_question = %s"
        cursor.execute(check_query, (question_id,))
        count = cursor.fetchone()[0]

        if count > 0:
            # Si hay respuestas, solo desactivar
            query = "UPDATE questions SET state = 'I' WHERE id = %s AND id_subject = %s"
            cursor.execute(query, (question_id, subject_id))
        else:
            # Si no hay respuestas, eliminar
            query = "DELETE FROM questions WHERE id = %s AND id_subject = %s"
            cursor.execute(query, (question_id, subject_id))

        cursor._connection.commit()
        return cursor.rowcount > 0
