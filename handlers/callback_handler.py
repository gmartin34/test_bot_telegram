from telebot.types import CallbackQuery
from keyboards.inline_buttons import buttons_play
from handlers.start_handler import quiz_sessions, send_question, iniciar_juego # Importamos la sesión del test
from database.db_connection import db_connection
from database.db_sql import register_answer

#  Maneja la respuesta del usuario

def callback_response(bot, call: CallbackQuery):
    chat_id = call.message.chat.id
    session = quiz_sessions.get(chat_id)

# IMPORTANTE: Registrar la respuesta en la base de datos
    student_id = session.get("student_id")
    
    # Manejar confirmacion de jugar
    if call.data.startswith("confirmar_jugar_"):
        # Eliminar el mensaje de confirmacion
        bot.delete_message(chat_id, call.message.message_id)
        
        # Iniciar el juego
        db = db_connection()
        iniciar_juego(bot, chat_id, db)
        db.close()
        
        # Responder al callback
        bot.answer_callback_query(call.id, "?Comenzando el juego!")
        return
    
    # Manejar cancelacion de jugar
    elif call.data.startswith("cancelar_jugar_"):
        # Eliminar el mensaje de confirmación
        bot.delete_message(chat_id, call.message.message_id)
        
        # Eliminar sesión si existe
        if chat_id in quiz_sessions:
            del quiz_sessions[chat_id]
        
        # Enviar mensaje de despedida
        bot.send_message(chat_id, "De acuerdo. Hasta la próxima!\n\nUsa /jugar cuando quieras comenzar.")
        
        # Responder al callback
        bot.answer_callback_query(call.id, "Juego cancelado")
        return
    # Manejar navegación en modo paginado
    elif call.data == "nav_prev":
        if not session or session.get("estado") != "jugando":
            bot.answer_callback_query(call.id, "❌ Sesión no válida")
            return
        
        current_page = session.get("current_option_page", 0)
        if current_page > 0:
            session["current_option_page"] = current_page - 1
            bot.delete_message(chat_id, call.message.message_id)
            send_question(bot, chat_id, db, student_id)
        bot.answer_callback_query(call.id)
        return
    
    elif call.data == "nav_next":
        if not session or session.get("estado") != "jugando":
            bot.answer_callback_query(call.id, "❌ Sesión no válida")
            return
        
        current_page = session.get("current_option_page", 0)
        total_options = session.get("total_options", 4)
        if current_page < total_options - 1:
            session["current_option_page"] = current_page + 1
            bot.delete_message(chat_id, call.message.message_id)
            send_question(bot, chat_id, db, student_id)
        bot.answer_callback_query(call.id)
        return
    
    # Manejar respuestas a preguntas (código existente)
    if call.data == "1" or call.data == "2" or call.data == "3" or call.data == "4":

        if not session or session.get("estado") != "jugando":
            bot.answer_callback_query(call.id, "? Sesión no válida. Usa /jugar para comenzar.")
            return

        # Obtener información de la pregunta actual
        current_question = quiz_sessions[chat_id]["questions"][session["current_index"]]
        question_id = current_question[0]  # ID de la pregunta
        correct_answer = current_question[5]  # Respuesta correcta
        reason = current_question[6]  # Motivo/explicación
        
        # Verificar si la respuesta es correcta
        is_correct = int(call.data) == correct_answer
        
        if is_correct:
            format_question_text = f"✅ Has respondido. ¡¡Enhorabuena!! \n <b>Motivo:</b> \n {reason}"
        else:
            format_question_text = f"❌ Respuesta incorrecta ¡Qué pena!! \n <b>Motivo:</b> \n {reason}"

        # Eliminar botones después de responder
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        bot.edit_message_text(f" {format_question_text} ", chat_id, call.message.message_id, parse_mode="HTML")
        

        if student_id:
            db = db_connection()
            success = register_answer(db, student_id, question_id, is_correct)
            print("Registro respuesta:", success)
            db.close()
            
            if not success:
                print(f"Error al registrar respuesta del estudiante {student_id} para pregunta {question_id}")
        
        # Avanzar a la siguiente pregunta
        session["current_index"] = session["current_index"] + 1
        session["message_id"] = call.message.message_id  # Actualizar message_id para la siguiente pregunta
        
        # Enviar siguiente pregunta
        send_question(bot, chat_id, db, student_id)