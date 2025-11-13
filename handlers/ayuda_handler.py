def handle_ayuda(bot, message):
    """
    Maneja el comando /ayuda mostrando todos los comandos disponibles
    """
    chat_id = message.chat.id
    
    mensaje_ayuda = """
📚 **AYUDA - TRIVIAL UNED BOT**

🎮 **COMANDOS DISPONIBLES:**

━━━━━━━━━━━━━━━━━━━━━━

📝 **/registro 'nombre apellidos' email**
Solicita tu registro en el sistema.
⚠️ Ejemplo: /registro 'Juan Pérez López' jperez@alumno.uned.es
📌 Requisito: Necesita aprobación del docente

━━━━━━━━━━━━━━━━━━━━━━

🎯 **/jugar**
Inicia el juego de trivial con preguntas de tu nivel actual.
📌 Requisito: Estar registrado y aprobado

━━━━━━━━━━━━━━━━━━━━━━

🏆 **/clasificacion**
Muestra tu posición en el ranking general basado en tu tasa de acierto.

━━━━━━━━━━━━━━━━━━━━━━

📊 **/visionado**
Muestra tus estadísticas personales:
- Preguntas respondidas
- Progreso completado
- Aciertos en primer y segundo intento

━━━━━━━━━━━━━━━━━━━━━━

📈 **/promocion**
Verifica si cumples los requisitos para subir de nivel.
✅ Debes completar todas las preguntas de tu nivel actual.

━━━━━━━━━━━━━━━━━━━━━━

👁️ **/vista [opc]**
Cambia el modo de visualización de las preguntas:
• /vista 1 - Modo extendido (pregunta + todas las opciones)
• /vista 2 - Modo paginado (navega entre opciones)

━━━━━━━━━━━━━━━━━━━━━━

❓ **/ayuda**
Muestra este mensaje de ayuda.

━━━━━━━━━━━━━━━━━━━━━━

💡 **CONSEJOS:**
• Responde correctamente en el primer intento para mejor ranking
• Completa todas las preguntas del nivel para promocionar
• Usa /visionado para seguir tu progreso

🎓 ¡Mucha suerte con el Trivial UNED!
"""
    
    bot.send_message(chat_id, mensaje_ayuda, parse_mode='Markdown')