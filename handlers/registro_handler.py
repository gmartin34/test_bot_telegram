import re
from database.db_sql import register_student, student_exists

def handle_registro(bot, message, db):
    """
    Maneja el comando /registro para nuevos estudiantes
    Formato: /registro 'nombre apellidos' email
    """
    chat_id = message.chat.id
    
    # Obtener el texto después del comando
    text = message.text.strip()
    
    # Verificar si ya está registrado
    if student_exists(db, chat_id):
        bot.send_message(chat_id, "✅ Usted ya está registrado en el sistema.")
        return
    
    # Expresión regular para extraer nombre y email
    # Formato: /registro 'nombre apellidos' email
    pattern = r"/registro\s+'([^']+)'\s+(\S+@\S+\.\S+)"
    match = re.match(pattern, text)
    
    if not match:
        bot.send_message(
            chat_id,
            "❌ Formato incorrecto. Use:\n"
            "/registro 'nombre apellidos' email\n\n"
            "Ejemplo: /registro 'Pablo Pérez García' pperez@alumno.uned.es"
        )
        return
    
    name = match.group(1)
    email = match.group(2)
    
    # Validar email básico
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        bot.send_message(chat_id, "❌ El email proporcionado no es válido.")
        return
    
    # Registrar estudiante
    if register_student(db, chat_id, name, email):
        bot.send_message(
            chat_id,
            f"✅ Registro exitoso!\n\n"
            f"👤 Nombre: {name}\n"
            f"📧 Email: {email}\n\n"
            f"⏳ Su solicitud está pendiente de validación por su tutor."
        )
    else:
        bot.send_message(
            chat_id,
            "❌ Error al registrar. Por favor, intente nuevamente o contacte al administrador."
        )