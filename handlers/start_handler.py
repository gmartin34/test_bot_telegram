"""
Handler principal para el comando /jugar
Gestiona el inicio de partidas, verificación de registro y envío de preguntas
"""

from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline_buttons import buttons_play
from database.db_sql import (
    load_questions_by_level, 
    check_student_registration, 
    chat_id_result,
    get_student_level,
    check_number_question_level,
    promote_student_level
)

# Diccionario global para guardar el progreso de cada usuario
# Estructura: {chat_id: {student_id, nivel, questions, current_index, estado, message_id}}
quiz_sessions = {}


def handle_jugar(bot, message: Message, db):
    """
    Maneja el comando /jugar
    Verifica el registro, estado y nivel del estudiante antes de iniciar la partida
    
    Args:
        bot: Instancia del bot de Telegram
        message: Mensaje recibido del usuario
        db: Conexión a la base de datos
    """
    chat_id = message.chat.id
    message_id = message.message_id
    
    print(f"\n{'='*60}")
    print(f"[JUGAR] Usuario {chat_id} solicitó jugar")
    print(f"{'='*60}")

    # Verificar registro del estudiante
    registration_status = check_student_registration(db, chat_id)
    print(f"[JUGAR] Estado de registro: {registration_status}")
    
    # Casos de registro no válido
    if registration_status is None:
        print(f"[JUGAR] Usuario {chat_id} no registrado")
        bot.send_message(
            chat_id, 
            "❌ *No estás registrado en el sistema*\n\n"
            "Para jugar, primero debes registrarte.\n\n"
            "📝 Usa el comando:\n"
            "`/registro 'Nombre Apellidos' email@ejemplo.com`\n\n"
            "Ejemplo:\n"
            "`/registro 'Pablo Pérez García' pperez@alumno.uned.es`",
            parse_mode='Markdown'
        )
        return
    
    if registration_status == 'P':
        print(f"[JUGAR] Usuario {chat_id} pendiente de aprobación")
        bot.send_message(
            chat_id, 
            "⏳ *Registro Pendiente*\n\n"
            "Tu solicitud de registro está pendiente de validación por tu tutor.\n\n"
            "Por favor, espera a que sea aprobada para poder jugar.\n\n"
            "📧 Recibirás una notificación cuando tu registro sea aprobado.",
            parse_mode='Markdown'
        )
        return
    
    elif registration_status == 'B':
        print(f"[JUGAR] Usuario {chat_id} dado de baja")
        bot.send_message(
            chat_id, 
            "🚫 *Acceso Denegado*\n\n"
            "Tu tutor te ha dado de baja en el sistema.\n\n"
            "Si crees que esto es un error, contacta con tu tutor.",
            parse_mode='Markdown'
        )
        return
    
    elif registration_status == 'A':
        # Usuario activo - Proceder con el juego
        print(f"[JUGAR] Usuario {chat_id} activo - Iniciando juego")
        
        # Obtener información del estudiante
        student_info = chat_id_result(db, chat_id)
        if not student_info:
            print(f"[JUGAR] ERROR: No se pudo obtener info del estudiante {chat_id}")
            bot.send_message(
                chat_id, 
                "❌ Error al obtener tu información.\n\n"
                "Por favor, intenta nuevamente o contacta con el administrador."
            )
            return
        
        student_id = student_info[0]
        student_name = student_info[1]
        print(f"[JUGAR] Estudiante: ID={student_id}, Nombre={student_name}")
        
        # Obtener nivel actual del estudiante
        nivel_actual = get_student_level(db, student_id)
        print(f"[JUGAR] Nivel actual del estudiante: {nivel_actual}")
        
        # Crear botones de confirmación
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("✅ SÍ, JUGAR", callback_data=f"confirmar_jugar_{chat_id}"),
            InlineKeyboardButton("❌ CANCELAR", callback_data=f"cancelar_jugar_{chat_id}")
        )
        
        # Mostrar mensaje de confirmación con información del nivel
        mensaje = f"""
🎮 *TRIVIAL UNED*

👤 Estudiante: *{student_name}*
📚 Nivel actual: *{nivel_actual}*


¿Deseas comenzar a jugar?

💡 Se te presentarán preguntas de tu nivel actual.
"""
        bot.send_message(
            chat_id, 
            mensaje, 
            parse_mode='Markdown', 
            reply_markup=markup
        )
        
        # Guardar información temporal para usar después de la confirmación
        quiz_sessions[chat_id] = {
            "student_id": student_id,
            "student_name": student_name,
            "nivel": nivel_actual,
            "estado": "esperando_confirmacion",
            "message_id": message_id,
            "questions": [],
            "current_index": 0
        }
        print(f"[JUGAR] Sesión creada para {chat_id} - Esperando confirmación")
        
    else:
        print(f"[JUGAR] Estado desconocido: {registration_status}")
        bot.send_message(
            chat_id, 
            "⚠️ Estado desconocido.\n\n"
            "Por favor, contacta con tu tutor."
        )


def iniciar_juego(bot, chat_id, db):
    """
    Inicia el juego después de la confirmación del usuario
    Carga las preguntas del nivel correspondiente y envía la primera
    
    Args:
        bot: Instancia del bot de Telegram
        chat_id: ID del chat del usuario
        db: Conexión a la base de datos
    """
    print(f"\n[INICIAR] Iniciando juego para usuario {chat_id}")
    
    session = quiz_sessions.get(chat_id)
    
    if not session or session["estado"] != "esperando_confirmacion":
        print(f"[INICIAR] ERROR: Sesión no válida para {chat_id}")
        bot.send_message(
            chat_id, 
            "❌ Error: sesión no válida.\n\n"
            "Por favor, usa /jugar para comenzar."
        )
        return
    
    # Cargar preguntas del nivel del estudiante
    nivel = session["nivel"]
    student_id = session["student_id"]
    print(f"[INICIAR] Cargando preguntas del nivel {nivel}")
    questions = load_questions_by_level(db, nivel, student_id)
    
    if not questions or len(questions) == 0:
        print(f"[INICIAR] No hay preguntas para el nivel {nivel}")
        bot.send_message(
            chat_id, 
            f"⚠️ *No hay preguntas disponibles*\n\n"
            f"No se encontraron preguntas activas para el nivel {nivel}.\n\n"
            f"Por favor, contacta con tu tutor.",
            parse_mode='Markdown'
        )
        del quiz_sessions[chat_id]
        return
    
    print(f"[INICIAR] Cargadas {len(questions)} preguntas del nivel {nivel}")
    
    # Actualizar sesión del usuario con las preguntas
    quiz_sessions[chat_id].update({
        "questions": questions,
        "current_index": 0,
        "estado": "jugando"
    })
    
    # Enviar mensaje de inicio
    bot.send_message(
        chat_id,
        f"🎯 *¡Comencemos!*\n\n"
        f"📚 Nivel: {nivel}\n"
        f"📝 Preguntas disponibles: {len(questions)}\n\n"
        f"¡Buena suerte! 🍀",
        parse_mode='Markdown'
    )
    
    # Enviar primera pregunta
    print(f"[INICIAR] Enviando primera pregunta")
    send_question(bot, chat_id, db, student_id)
    

def send_question(bot, chat_id, db, student_id):
    """
    Envía la siguiente pregunta al usuario
    Controla el flujo del cuestionario y el formato de las preguntas
    
    Args:
        bot: Instancia del bot de Telegram
        chat_id: ID del chat del usuario
    """
    print("Informacion Args:", bot, chat_id, db, student_id)
    session = quiz_sessions.get(chat_id)
    
    if not session:
        print(f"[PREGUNTA] ERROR: No existe sesión para {chat_id}")
        bot.send_message(
            chat_id,
            "❌ Error: No hay sesión activa.\n\n"
            "Usa /jugar para comenzar."
        )
        return
    
    # Verificar si quedan preguntas
    if session["current_index"] >= len(session["questions"]):
        
        
        # Verificar completitud del nivel actual
        db.reconnect()
        total_preguntas, preguntas_respondidas, nivel = check_number_question_level(db, student_id)
        print(f"[PREGUNTA] Nivel completado: {preguntas_respondidas}/{total_preguntas} preguntas respondidas")
        if preguntas_respondidas != 0:            
            bot.send_message(
                chat_id, 
                "🎉 *¡Felicitaciones!*\n\n"
                "Has contestado a la tanda de preguntas propuestas.\n\n"
                "📊 Usa /misnumeros para ver tus estadísticas\n"
                "🏆 Usa /clasificacion para ver tu posición en el ranking\n"
                "⬆️ Usa /promocion para verificar si puedes subir de nivel",
                parse_mode='Markdown'
            )
        else:
            promote_student_level(db, student_id)
            bot.send_message(
                chat_id,
                 "🎉 *¡Felicitaciones!*\n\n"
                 f"Has subido al nivel {nivel + 1}.\n\n" 
                "📊 Usa /misnumeros para ver tus estadísticas\n"
                "🏆 Usa /clasificacion para ver tu posición en el ranking\n"
                "⬆️ Usa /promocion para verificar si puedes subir de nivel",
                parse_mode='Markdown'
            )

        # Limpiar sesión
        db.close()
        del quiz_sessions[chat_id]
        return
    
    # Obtener datos de la pregunta actual
    current_index = session["current_index"]
    question_data = session["questions"][current_index]
    
    # Estructura de question_data (según tabla questions):
    # [0] = id, [1] = id_subject, [2] = state, [3] = level, [4] = question,
    # [5] = solution, [6] = why, [7] = answer1, [8] = answer2, 
    # [9] = answer3, [10] = answer4
    
    question_id = question_data[0]
    question_text = question_data[4]
    opcion1 = question_data[7]
    opcion2 = question_data[8]
    opcion3 = question_data[9]
    opcion4 = question_data[10]
    
    print(f"[PREGUNTA] Enviando pregunta {current_index + 1}/{len(session['questions'])} (ID: {question_id}) a {chat_id}")
    
    # Crear el markup con botones
    #markup = buttons_play()
    
    # Formatear el mensaje según el número de opciones
    if opcion3 is None or opcion4 is None:
        # Solo 2 opciones
        format_question_text = (
            f"📚 *Nivel {session['nivel']}* | "
            f"Pregunta {current_index + 1}/{len(session['questions'])}\n\n"
            f"*{question_text}*\n\n"
            f"🔴 *Opción 1:* {opcion1}\n"
            f"🔵 *Opción 2:* {opcion2}\n"
        )
        cuatro_opciones = False
    else:
        # 4 opciones
        format_question_text = (
            f"📚 *Nivel {session['nivel']}* | "
            f"Pregunta {current_index + 1}/{len(session['questions'])}\n\n"
            f"*{question_text}*\n\n"
            f"🔴 *Opción 1:* {opcion1}\n"
            f"🔵 *Opción 2:* {opcion2}\n"
            f"🟢 *Opción 3:* {opcion3}\n"
            f"🟣 *Opción 4:* {opcion4}\n"
        )
        cuatro_opciones = True
    
    # Crear el markup con botones
    markup = buttons_play(cuatro_opciones)
    
    # Enviar pregunta
    sent_message = bot.send_message(
        chat_id, 
        format_question_text, 
        parse_mode='Markdown', 
        reply_markup=markup
    )
    
    # Actualizar message_id en la sesión
    session["message_id"] = sent_message.message_id
    print(f"[PREGUNTA] Pregunta enviada exitosamente")


def get_session(chat_id):
    """
    Obtiene la sesión activa de un usuario
    
    Args:
        chat_id: ID del chat del usuario
        
    Returns:
        dict: Sesión del usuario o None si no existe
    """
    return quiz_sessions.get(chat_id)


def delete_session(chat_id):
    """
    Elimina la sesión de un usuario
    
    Args:
        chat_id: ID del chat del usuario
    """
    if chat_id in quiz_sessions:
        print(f"[SESSION] Eliminando sesión para {chat_id}")
        del quiz_sessions[chat_id]
        

def get_current_question_id(chat_id):
    """
    Obtiene el ID de la pregunta actual para un usuario
    
    Args:
        chat_id: ID del chat del usuario
        
    Returns:
        int: ID de la pregunta actual o None
    """
    session = quiz_sessions.get(chat_id)
    if session and session["estado"] == "jugando":
        current_index = session["current_index"]
        if current_index < len(session["questions"]):
            return session["questions"][current_index][0]  # ID de la pregunta
    return None