
# inline buttons

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def buttons_play():
    
    keyboard = [
        [ InlineKeyboardButton("🔴 Opción 1", callback_data='1',
                                test='uno',
                                style='background-colo: red;color: white;'),
          InlineKeyboardButton("🔵 Opción 2", callback_data='2',
                                test='dos',
                                style='background-colo: blue;color: white;'),
          InlineKeyboardButton("🟢 Opción 3", callback_data='3',
                                test='tres',
                                style='background-colo: green;color: white;'),  
          InlineKeyboardButton("🟣 Opción 4", callback_data='4',
                                test='cuatro',
                                style='background-colo: purple;color: white;')                                          
          ]
    #   [
    #     InlineKeyboardButton("➡️ Opción", callback_data="next"),
    #     InlineKeyboardButton("✅ Respuesta", callback_data="question"),
    #     InlineKeyboardButton("⬅️ Opción", callback_data="back")
    #   ]
    
     ]
    #recibe el mensaje

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
# Añadir los botones al teclado

    
 