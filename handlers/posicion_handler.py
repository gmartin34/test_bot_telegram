from database.db_sql import query_ranking, chat_id_result, check_student_registration

def handle_posicion(bot, message, db):
    """
    Maneja el comando /clasificacion mostrando la posición del estudiante
    basándose en su tasa de acierto comparada con otros estudiantes
    """
    try:
        # Obtener el chat_id del usuario
        chat_id = message.chat.id
        print(f"Comando clasificacion Chat ID del usuario: {chat_id}")
        
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
            # Usuario activo, mostrar ranking
            # Buscar el id del estudiante usando el chat_id
            id_student = chat_id_result(db, chat_id)
            print(f"Comando posicion ID del estudiante: {id_student}")
            

            if not id_student:
                # Si no se encuentra el estudiante, enviar mensaje de error
                bot.send_message(chat_id, "❌ Error al obtener información del estudiante.")
                return
            
            student_id = id_student[0]
            student_name = id_student[1]
            print(f"Nombre: {student_name}")  
            
            # Calcular la tasa de acierto para todos los estudiantes
            rankings = query_ranking(db)

            print(f"Ranking obtenido: {rankings}")
            if not rankings:
                bot.send_message(chat_id, "📊 Aún no hay datos suficientes para generar el ranking.")
                return
            
            # Encontrar la posición del estudiante
            posicion = 0
            mi_tasa_acierto = 0
            mi_preguntas = 0
            total_estudiantes = len(rankings)
            
            for idx, (est_id, nombre, preguntas, intentos, errores, tasa) in enumerate(rankings):
                if est_id == student_id:
                    posicion = idx + 1
                    mi_tasa_acierto = tasa
                    mi_preguntas = preguntas
                    break
            
            if posicion == 0:
                # El estudiante no ha respondido ninguna pregunta aún
                mensaje = f"""
📊 **POSICIÓN EN EL RANKING**

👤 Estudiante: {student_name}

❗ Aún no has respondido ninguna pregunta.
¡Comienza a jugar para aparecer en el ranking!

📈 Total de participantes activos: {total_estudiantes}
"""
            else:
                # Calcular percentil
                percentil = round(((total_estudiantes - posicion + 1) / total_estudiantes) * 100, 1)
                
                # Determinar medalla según posición
                if posicion == 1:
                    medalla = "🥇"
                elif posicion == 2:
                    medalla = "🥈"
                elif posicion == 3:
                    medalla = "🥉"
                elif posicion <= 10:
                    medalla = "🏆"
                else:
                    medalla = "📊"
                
                # Obtener información del top 3
                top_3_info = ""
                for idx in range(min(3, len(rankings))):
                    est_id, nombre, preguntas, intentos, errores, tasa = rankings[idx]
                    if idx == 0:
                        emoji = "🥇"
                    elif idx == 1:
                        emoji = "🥈"
                    else:
                        emoji = "🥉"
                    top_3_info += f"{emoji} {nombre}: {tasa}% de acierto\n"
                
                mensaje = f"""
📊 **POSICIÓN EN EL RANKING**

{medalla} **Tu posición: {posicion} de {total_estudiantes}**

👤 Estudiante: {student_name}
✅ Tasa de acierto: {mi_tasa_acierto}%
📝 Preguntas respondidas: {mi_preguntas}
📈 Percentil: Top {percentil}%


"""
                
                # Si está cerca del siguiente puesto, mostrar motivación
                if posicion > 1:
                    siguiente_tasa = rankings[posicion-2][5]
                    diferencia = round(siguiente_tasa - mi_tasa_acierto, 2)
                    if diferencia <= 5:
                        mensaje += f"\n💪 ¡Estás a solo {diferencia}% del siguiente puesto!"
            
            # Enviar el mensaje
            bot.send_message(chat_id, mensaje, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Error en handle_posicion: {e}")
        bot.send_message(message.chat.id, "❌ Ha ocurrido un error al obtener tu posición.")
    finally:
        print("Comando /clasificacion procesado correctamente.")