from database.db_sql import check_student_registration, chat_id_result, update_view_mode

def handle_vista(bot, message, db):
    """
    Maneja el comando /vista para cambiar el modo de visualización de preguntas
    Formato: /vista [1|2]
    1 = Modo extendido (pregunta + todas las opciones)
    2 = Modo paginado (navegar entre opciones)
    """
    chat_id = message.chat.id
    
    # Verificar registro del estudiante
    registration_status = check_student_registration(db, chat_id)
    
    if registration_status is None:
        bot.send_message(
            chat_id, 
            "❌ Por favor, regístrese primero usando:\n"
            "/registro 'nombre_apellidos' email\n\n"
            "Ejemplo: /registro 'Pablo Pérez García' pperez@alumno.uned.es"
        )
        return
    
    if registration_status == 'P':
        bot.send_message(chat_id, "⏳ Pendiente de validación por su tutor")
        return
    elif registration_status == 'B':
        bot.send_message(chat_id, "🚫 Su tutor le ha dado de baja en el juego")
        return
    
    # Usuario activo
    if registration_status == 'A':
        # Obtener información del estudiante
        student_info = chat_id_result(db, chat_id)
        if not student_info:
            bot.send_message(chat_id, "❌ Error al obtener información del estudiante")
            return
        
        student_id = student_info[0]
        
        # Obtener el parámetro del comando
        text = message.text.strip().split()
        
        if len(text) != 2:
            bot.send_message(
                chat_id,
                "❌ Formato incorrecto. Use:\n\n"
                "👁️ **/vista 1** - Modo extendido\n"
                "  (Muestra pregunta + todas las opciones)\n\n"
                "👁️ **/vista 2** - Modo paginado\n"
                "  (Navega entre opciones con botones)\n\n"
                "Ejemplo: /vista 1",
                parse_mode='Markdown'
            )
            return
        
        opcion = text[1]
        
        if opcion not in ['1', '2']:
            bot.send_message(
                chat_id,
                "❌ Opción no válida. Use:\n"
                "• /vista 1 para modo extendido\n"
                "• /vista 2 para modo paginado"
            )
            return
        
        # Actualizar modo de vista en la base de datos
        if update_view_mode(db, student_id, opcion):
            modo_nombre = "Extendido" if opcion == '1' else "Paginado"
            modo_descripcion = (
                "📋 Verás la pregunta y todas las opciones juntas" 
                if opcion == '1' 
                else "📖 Navegarás entre las opciones con botones ◀️ ▶️"
            )
            
            mensaje = f"""
✅ **Modo de vista actualizado**

👁️ Modo seleccionado: **{modo_nombre}**

{modo_descripcion}

💡 Este cambio se aplicará la próxima vez que uses /jugar

🎮 ¿Listo para jugar? Usa /jugar
"""
            bot.send_message(chat_id, mensaje, parse_mode='Markdown')
        else:
            bot.send_message(
                chat_id,
                "❌ Error al actualizar el modo de vista. Intente nuevamente."
            )