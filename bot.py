import asyncio
import threading
from config import TELEGRAM_TOKEN
import telebot
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram import Update, BotCommand

# Instanciar el bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Importar los manejadores de comandos
from handlers.start_handler import handle_jugar
from handlers.callback_handler import callback_response
from handlers.posicion_handler import handle_posicion
from handlers.registro_handler import handle_registro
from handlers.visionado_handler import handle_visionado
from handlers.promocion_handler import handle_promocion
from database.db_connection import db_connection

# Importar la aplicación Flask del dashboard
from dashboard.app import app

# Función para ejecutar el servidor Flask en un hilo separado
def run_dashboard():
    """Ejecuta el servidor Flask del dashboard en modo no-reload"""
    print("Iniciando el dashboard...")
    app.run(debug=True, use_reloader=False, port=5000, host='0.0.0.0')


# ========== MANEJADORES DE COMANDOS DE TELEBOT ==========

@bot.message_handler(commands=['jugar'])
def jugar_command(message):
    """Manejador del comando /jugar"""
    db = db_connection()
    try:
        handle_jugar(bot, message, db)
    finally:
        db.close()


@bot.message_handler(commands=['clasificacion'])
def clasificacion_command(message):
    """Manejador del comando /clasificacion"""
    db = db_connection()
    try:
        handle_posicion(bot, message, db)
    finally:
        db.close()


@bot.message_handler(commands=['registro'])
def registro_command(message):
    """Manejador del comando /registro"""
    db = db_connection()
    try:
        handle_registro(bot, message, db)
    finally:
        db.close()


@bot.message_handler(commands=['misnumeros'])
def visionado_command(message):
    """Manejador del comando /misnumeros"""
    db = db_connection()
    try:
        handle_visionado(bot, message, db)
    finally:
        db.close()


@bot.message_handler(commands=['promocion'])
def promocion_command(message):
    """Manejador del comando /promocion"""
    db = db_connection()
    try:
        handle_promocion(bot, message, db)
    finally:
        db.close()


@bot.message_handler(commands=['start', 'ayuda'])
def help_command(message):
    """Manejador de comandos de ayuda e inicio"""
    help_text = """
🎮 **BIENVENIDO AL TRIVIAL UNED** 🎮

📚 Comandos disponibles:

/jugar - Iniciar una partida de preguntas
/clasificacion - Ver tu posición en el ranking
/visionado - Consultar tus estadísticas
/promocion - Verificar promoción de nivel
/registro - Registrarse en el sistema
/ayuda - Mostrar esta ayuda

💡 Para comenzar, usa /registro si es tu primera vez
o /jugar si ya estás registrado.

¡Buena suerte! 🍀
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


# Manejador de botones inline (callbacks)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Manejador de todos los callbacks de botones inline"""
    callback_response(bot, call)


# ========== FUNCIONES ASÍNCRONAS PARA PYTHON-TELEGRAM-BOT ==========
# (Estas son para futura expansión o comandos adicionales si se necesitan)

async def start_async(update: Update, context: CallbackContext) -> None:
    """Handler asíncrono alternativo para /start"""
    await update.message.reply_text(
        "¡Hola! Soy tu bot de Telegram. Usa /ayuda para ver los comandos disponibles."
    )


async def help_async(update: Update, context: CallbackContext) -> None:
    """Handler asíncrono alternativo para /ayuda"""
    help_text = """
Lista de comandos:
/jugar - Iniciar juego
/ayuda - Mostrar ayuda
/clasificacion - Ver ranking
/registro - Registrarse
/misnumeros - Ver estadísticas
/promocion - Ver promociones
    """
    await update.message.reply_text(help_text)
    

async def set_commands(application: Application):
    """Configura los comandos del bot en el menú de Telegram"""
    commands = [
        BotCommand("jugar", "Iniciar juego"),
        BotCommand("ayuda", "Mostrar ayuda"),
        BotCommand("clasificacion", "Mostrar Clasificación"),
        BotCommand("registro", "Registrarse en el sistema"),
        BotCommand("misnumeros", "Ver estadísticas"),
        BotCommand("promocion", "Ver promociones"),
    ]
    await application.bot.set_my_commands(commands)

async def main_async():
    """Función principal asíncrona para configurar comandos adicionales"""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Configurar comandos antes de iniciar
    await set_commands(application)
    
    # Agregar handlers asíncronos (opcional, para expansión futura)
    application.add_handler(CommandHandler("start", start_async))
    application.add_handler(CommandHandler("ayuda", help_async))
    
    print("Comandos asíncronos configurados")


# ========== FUNCIÓN PRINCIPAL ==========

if __name__ == '__main__':
    print('=' * 60)
    print('INICIANDO SISTEMA TRIVIAL UNED')
    print('=' * 60)
    
    # Conectar a la base de datos para verificar conexión
    print('\n[1/3] Conectando a la base de datos...')
    db = db_connection()
    if db and db.is_connected():
        print('✓ Conexión a la base de datos exitosa')
        db.close()
    else:
        print('✗ Error al conectar a la base de datos')
        exit(1)
    
    # Configurar comandos del bot de forma asíncrona
    print('\n[2/3] Configurando comandos del bot...')
    try:
        asyncio.run(main_async())
        print('✓ Comandos del bot configurados')
    except Exception as e:
        print(f'⚠️ Advertencia al configurar comandos: {e}')
    
    # Iniciar el servidor Flask del dashboard en un hilo separado
    print('\n[3/3] Iniciando dashboard web...')
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    print('✓ Dashboard web iniciado en http://localhost:5000/dashboard/')
    
    # Iniciar el bot con polling infinito
    print('\n' + '=' * 60)
    print('✓ SISTEMA COMPLETAMENTE OPERATIVO')
    print('=' * 60)
    print('\nBot escuchando mensajes...')
    print('Dashboard disponible en: http://localhost:5000/dashboard/')
    print('\nPresiona Ctrl+C para detener el sistema\n')
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print('\n\nDeteniendo el sistema...')
        print('¡Hasta luego!')
    except Exception as e:
        print(f'\n\n✗ Error en el bot: {e}')
        print('Reiniciando...')