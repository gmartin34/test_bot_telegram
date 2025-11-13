
from config import * # importamos variable de entorno o configuraciones

#Query de preguntas
def load_questions(db):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()  # Obtiene todos los registros


    cursor.close()
    return questions

# Comprobación de la existencia del estudiante
def chat_id_result(db, chat_id):
    cursor = db.cursor()
    query = "SELECT id, name FROM students WHERE cid = %s"
    cursor.execute(query, (chat_id,))
    result = cursor.fetchone()
    print(f"Resultado de la consulta para chat_id {chat_id}: {result}")
    cursor.close()
    return result if result else None  # Devuelve el ID del estudiante o None si no existe   

# Ranking de estudiantes    
def query_ranking(db):
    cursor = db.cursor()
    query = """
    SELECT
        sq.id_student,
        s.name,
        COUNT(DISTINCT sq.id_question) as preguntas_respondidas,
        SUM(sq.num_attempts) as total_intentos,
        SUM(sq.mistake_number) as total_errores,
        CASE
            WHEN SUM(sq.num_attempts) > 0
            THEN ROUND((1 - (SUM(sq.mistake_number) / SUM(sq.num_attempts))) * 100, 2)
            ELSE 0
        END as tasa_acierto
    FROM student_question sq
    INNER JOIN students s ON sq.id_student = s.id
    GROUP BY sq.id_student, s.name
    HAVING SUM(sq.num_attempts) > 0
    ORDER BY tasa_acierto DESC, preguntas_respondidas DESC
    """
    cursor.execute(query)
    rankings = cursor.fetchall()
    cursor.close()
    return rankings
# Verificar registro del estudiante
def check_student_registration(db, chat_id):
    cursor = db.cursor()
    # Primero verificar si existe el estudiante
    query = "SELECT id FROM students WHERE cid = %s"
    cursor.execute(query, (chat_id,))
    result = cursor.fetchone()
    
    if not result:
        cursor.close()
        return None  # No está registrado
    
    student_id = result[0]
    
    # Verificar estado en student_subject
    query = """
    SELECT state 
    FROM student_subject 
    WHERE id_student = %s 
    ORDER BY id DESC 
    LIMIT 1
    """
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()
    cursor.close()
    
    if result:
        return result[0]  # Retorna 'A', 'P' o 'B'
    else:
        return None  # No tiene registro en student_subject

# Registrar nuevo estudiante
def register_student(db, chat_id, name, email):
    cursor = db.cursor()
    try:
        # Insertar en students
        query = "INSERT INTO students (cid, name, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (chat_id, name, email))
        student_id = cursor.lastrowid
        
        # Insertar en student_subject con state='P' para todas las asignaturas activas
        query = """
        INSERT INTO student_subject (id_student, id_subject, state, level) 
        SELECT %s, id, 'P', 1 
        FROM subject 
        WHERE status = 'A'
        """
        cursor.execute(query, (student_id,))
        
        db.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error en registro: {e}")
        db.rollback()
        cursor.close()
        return False

# Verificar si el estudiante ya existe
def student_exists(db, chat_id):
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM students WHERE cid = %s"
    cursor.execute(query, (chat_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

# Obtener nivel actual del estudiante
def get_student_level(db, student_id):
    cursor = db.cursor()
    query = "SELECT level FROM student_subject WHERE id_student = %s LIMIT 1"
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else 1  # Por defecto nivel 1

# Cargar preguntas por nivel
def load_questions_by_level(db, level):
    cursor = db.cursor()
    query = "SELECT * FROM questions WHERE level = %s AND state = 'A'"
    cursor.execute(query, (level,))
    questions = cursor.fetchall()
    cursor.close()
    return questions

# Verificar si el estudiante completó todas las preguntas del nivel
def check_level_completion(db, student_id, level):
    cursor = db.cursor()
    
    # Total de preguntas del nivel
    query_total = "SELECT COUNT(*) FROM questions WHERE level = %s AND state = 'A'"
    cursor.execute(query_total, (level,))
    total_questions = cursor.fetchone()[0]
    
    # Preguntas respondidas por el estudiante en ese nivel
    query_answered = """
    SELECT COUNT(DISTINCT sq.id_question) 
    FROM student_question sq
    JOIN questions q ON sq.id_question = q.id
    WHERE sq.id_student = %s AND q.level = %s
    """
    cursor.execute(query_answered, (student_id, level))
    answered_questions = cursor.fetchone()[0]
    
    cursor.close()
    return total_questions, answered_questions

# Verificar si existe un nivel superior
def exists_next_level(db, current_level):
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM questions WHERE level = %s AND state = 'A'"
    cursor.execute(query, (current_level + 1,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

# Promover estudiante al siguiente nivel
def promote_student_level(db, student_id):
    cursor = db.cursor()
    try:
        query = "UPDATE student_subject SET level = level + 1 WHERE id_student = %s"
        cursor.execute(query, (student_id,))
        db.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error al promover estudiante: {e}")
        db.rollback()
        cursor.close()
        return False

# Obtener nivel máximo del juego
def get_max_level(db):
    cursor = db.cursor()
    query = "SELECT MAX(level) FROM questions WHERE state = 'A'"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result[0] else 1
    
def register_answer(db, student_id, question_id, is_correct, attempt_number=1):
    """
    Registra la respuesta de un estudiante a una pregunta
    """
    cursor = db.cursor()
    try:
        # Verificar si ya existe un registro para esta pregunta
        check_query = """
        SELECT id, num_attempts, mistake_number, first_attempt, second_attempt 
        FROM student_question 
        WHERE id_student = %s AND id_question = %s
        """
        cursor.execute(check_query, (student_id, question_id))
        existing = cursor.fetchone()
        
        if existing:
            # Actualizar registro existente
            record_id = existing[0]
            num_attempts = existing[1] + 1
            mistake_number = existing[2] + (0 if is_correct else 1)
            first_attempt = existing[3]
            second_attempt = existing[4]
            
            # Actualizar intentos
            if num_attempts == 1:
                first_attempt = 1 if is_correct else 0
            elif num_attempts == 2:
                second_attempt = 1 if is_correct else 0
            
            update_query = """
            UPDATE student_question 
            SET num_attempts = %s, 
                mistake_number = %s, 
                first_attempt = %s,
                second_attempt = %s,
                last_attempt_date = CURDATE()
            WHERE id = %s
            """
            cursor.execute(update_query, (num_attempts, mistake_number, first_attempt, second_attempt, record_id))
        else:
            # Insertar nuevo registro
            insert_query = """
            INSERT INTO student_question 
            (id_student, id_question, mistake_number, num_attempts, first_attempt, second_attempt, first_attempt_date, last_attempt_date)
            VALUES (%s, %s, %s, %s, %s, %s, CURDATE(), CURDATE())
            """
            mistake_number = 0 if is_correct else 1
            first_attempt = 1 if is_correct else 0
            cursor.execute(insert_query, (student_id, question_id, mistake_number, 1, first_attempt, 0))
        
        db.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error al registrar respuesta: {e}")
        db.rollback()
        cursor.close()
        return False
    
# Actualizar modo de vista del estudiante   
def update_view_mode(db, student_id, mode):
    cursor = db.cursor()
    try:
        query = "UPDATE students SET view_mode = %s WHERE id = %s"
        cursor.execute(query, (mode, student_id))
        db.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error al actualizar modo de vista: {e}")
        db.rollback()
        cursor.close()
        return False

# Obtener modo de vista del estudiante
def get_view_mode(db, student_id):
    cursor = db.cursor()
    query = "SELECT view_mode FROM students WHERE id = %s"
    cursor.execute(query, (student_id,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else '1'  # Por defecto modo '1' (Extendido)     

