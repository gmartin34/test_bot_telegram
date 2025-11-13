from database.db_sql import (
    check_student_registration, 
    chat_id_result, 
    get_student_level,
    check_level_completion,
    exists_next_level,
    promote_student_level,
    get_max_level
)

def handle_promocion(bot, message, db):
    """
    Maneja el comando /promocion para gestionar la subida de nivel del estudiante
    """
    chat_id = message.chat.id
    
    # Verificar registro del estudiante
    registration_status = check_student_registration(db, chat_id)
    
    if registration_status is None:
        bot.send_message(
            chat_id, 
            "❌ Por favor, regístrese. Puede solicitar el registro con el comando:\n"
            "/registro 'nombre_apellidos' email\n\n"
            "Ejemplo: /registro 'Pablo Pérez García' pperez@alumno.uned.es"
        )
        return
    
    if registration_status == 'P':
        bot.send_message(chat_id, "⏳ Pendiente de validación por su tutor, espere la respuesta")
        return
    elif registration_status == 'B':
        bot.send_message(chat_id, "🚫 Su tutor le ha dado de baja en el juego")
        return
    elif registration_status == 'A':
        # Usuario activo, verificar promoción
        
        # Obtener información del estudiante
        student_info = chat_id_result(db, chat_id)
        if not student_info:
            bot.send_message(chat_id, "❌ Error al obtener información del estudiante")
            return
        
        student_id = student_info[0]
        student_name = student_info[1]
        
        # Obtener nivel actual
        nivel_actual = get_student_level(db, student_id)
        
        # Verificar completitud del nivel actual
        total_preguntas, preguntas_respondidas = check_level_completion(db, student_id, nivel_actual)
        
        # Verificar si completó todas las preguntas del nivel
        if preguntas_respondidas < total_preguntas:
            faltantes = total_preguntas - preguntas_respondidas
            mensaje = f"""
📊 **ESTADO DE PROMOCIÓN**

👤 Estudiante: {student_name}
📖 Nivel actual: {nivel_actual}

⚠️ **No puedes promocionar todavía**

❌ Has respondido {preguntas_respondidas} de {total_preguntas} preguntas
📝 Te faltan {faltantes} pregunta{'s' if faltantes > 1 else ''} por responder

💪 ¡Continúa jugando para completar el nivel!
🎮 Usa /jugar para seguir avanzando
"""
            bot.send_message(chat_id, mensaje, parse_mode='Markdown')
            return
        
        # Verificar si existe siguiente nivel
        if not exists_next_level(db, nivel_actual):
            # Obtener nivel máximo
            nivel_maximo = get_max_level(db)
            mensaje = f"""
🏆 **¡FELICITACIONES!**

👤 Estudiante: {student_name}
🎯 Nivel actual: {nivel_actual} (Nivel máximo)

🌟 **¡Has alcanzado el nivel máximo del juego!**
✅ Has completado todas las {total_preguntas} preguntas del nivel {nivel_actual}

🎉 ¡Eres un verdadero maestro del Trivial UNED!
👏 Has demostrado dominio total del contenido

📊 Usa /visionado para ver tus estadísticas completas
🏅 Usa /clasificacion para ver tu posición en el ranking
"""
            bot.send_message(chat_id, mensaje, parse_mode='Markdown')
            return
        
        # Promocionar al estudiante
        if promote_student_level(db, student_id):
            nuevo_nivel = nivel_actual + 1
            mensaje = f"""
🎊 **¡PROMOCIÓN EXITOSA!**

👤 Estudiante: {student_name}

✅ **Has sido promovido al Nivel {nuevo_nivel}**

🎯 Completaste todas las {total_preguntas} preguntas del Nivel {nivel_actual}
📈 Ahora jugarás con preguntas del Nivel {nuevo_nivel}

🎮 Usa /jugar para comenzar con las nuevas preguntas
💪 ¡Sigue así y alcanza el nivel máximo!
"""
            bot.send_message(chat_id, mensaje, parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "❌ Error al promocionar. Contacte con el administrador.")