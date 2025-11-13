from database.db_sql import check_student_registration, chat_id_result

def handle_visionado(bot, message, db):
    """
    Maneja el comando /visionado para mostrar estadísticas del estudiante
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
        # Usuario activo, mostrar estadísticas
        student_info = chat_id_result(db, chat_id)
        if not student_info:
            bot.send_message(chat_id, "❌ Error al obtener información del estudiante")
            return
        
        student_id = student_info[0]
        student_name = student_info[1]
        
        # Obtener estadísticas del estudiante
        cursor = db.cursor()
        query = """
        SELECT 
            COUNT(DISTINCT sq.id_question) as preguntas_respondidas,
            SUM(sq.num_attempts) as total_intentos,
            SUM(CASE WHEN sq.first_attempt = 1 THEN 1 ELSE 0 END) as aciertos_primer_intento,
            SUM(CASE WHEN sq.second_attempt = 1 THEN 1 ELSE 0 END) as aciertos_segundo_intento,
            (SELECT COUNT(*) FROM questions WHERE state = 'A') as total_preguntas
        FROM student_question sq
        WHERE sq.id_student = %s
        """
        cursor.execute(query, (student_id,))
        stats = cursor.fetchone()
        cursor.close()
        
        if stats and stats[0] > 0:
            preguntas_respondidas = stats[0]
            total_intentos = stats[1]
            aciertos_primer = stats[2]
            aciertos_segundo = stats[3]
            total_preguntas = stats[4]
            
            porcentaje_completado = (preguntas_respondidas / total_preguntas * 100) if total_preguntas > 0 else 0
            porcentaje_acierto_primero = (aciertos_primer / preguntas_respondidas * 100) if preguntas_respondidas > 0 else 0
            
            mensaje = f"""
📊 **ESTADÍSTICAS DE {student_name.upper()}**

📝 Preguntas respondidas: {preguntas_respondidas} de {total_preguntas}
📈 Progreso: {porcentaje_completado:.1f}%
🎯 Total de intentos: {total_intentos}
✅ Aciertos primer intento: {aciertos_primer} ({porcentaje_acierto_primero:.1f}%)
✔️ Aciertos segundo intento: {aciertos_segundo}

¡Sigue así! 💪
"""
        else:
            mensaje = f"""
📊 **ESTADÍSTICAS DE {student_name.upper()}**

Aún no has respondido ninguna pregunta.
¡Usa /jugar para comenzar! 🎮
"""
        
        bot.send_message(chat_id, mensaje, parse_mode='Markdown')