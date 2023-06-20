from config import *    #importamos el token y los id de grupo
import telebot  #para manejar la API de Telegram
import threading
from fun_cumples import * #para las funciones de los cumples
from juego import * #para el juego del ahorcado
from telebot.types import ReplyKeyboardMarkup   #botones y demás
from telebot.types import ForceReply    #citar un mensaje
import os   #para borrar lineas en un fichero
from datetime import datetime   #para el manejo de horas
from pytz import timezone     #para las franjas horarias
import mysql.connector #Para la base de datos

#Instanciamos el bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

#Conectamos base de datos
import mysql.connector

# Establecer la conexión con la base de datos
conn = mysql.connector.connect(
    user='eleeeena1204',
    password='ElenaTFG2023',
    host='127.0.0.1',
    database='bot_telegram'
)

#Responder a los comandos
@bot.message_handler(commands=["start", "iniciar"])
def cmd_start(message):
    '''Da la bienvenida al usuario del bot'''
    if MY_CHAT_ID == message.chat.id:
        bot.send_message(message.chat.id, "HOLA!\nSoy tu bot de cumpleaños, añade el tuyo para felicitarte.")
    print(message.chat.id)
    
@bot.message_handler(commands=["help", "ayuda"])
def cmd_help(message):
    '''Muestra la lista de comandos'''
    if MY_CHAT_ID == message.chat.id:
        text = '<b><u>AYUDA</u></b>' + '\n'
        text += 'Estos son los comandos disponibles:' + '\n'
        text += '✰ /start o /iniciar → da la bienvenida' + '\n'
        text += '✰ /help o /ayuda → muestra lista de comandos disponibles' + '\n'
        text += '✰ /add o /nuevo → añade cumpleaños' + '\n'
        text += '✰ /view o /ver → muestra el cumpleaños del usuario' + '\n'
        text += '✰ /delete o /borrar → borrar un cumpleaños' + '\n'
        text += '✰ /test o /probar → ejemplo del mensaje de cumpleaños' + '\n'
        text += '✰ /hangman o /ahorcado → jugar al juego del ahorcado' + '\n'

        bot.send_message(message.chat.id, text, parse_mode='html')

entrada = []
@bot.message_handler(commands=["add", "nuevo"])    
def cmd_add(message):
    '''Añadimos un nuevo cumpleaños'''
    if MY_CHAT_ID == message.chat.id:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres añadir el cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
        bot.register_next_step_handler(msg, preguntar_zona_horaria, bot, entrada)   
    
@bot.message_handler(commands=["view", "ver"])    
def cmd_view(message):
    '''Muestra cuando es el cumpleaños de un usuario'''
    if MY_CHAT_ID == message.chat.id:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver cuándo es su cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
        bot.register_next_step_handler(msg, mostrar_cumple, bot)    

@bot.message_handler(commands=["delete", "borrar"])    
def cmd_delete(message):
    '''Borrar un cumpleaños'''
    if MY_CHAT_ID == message.chat.id:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres borrar el cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
        bot.register_next_step_handler(msg, borrar_cumple, bot)    

@bot.message_handler(commands=["test", "probar"])    
def cmd_test(message):
    '''Prueba el mensaje de cumpleaños'''
    if MY_CHAT_ID == message.chat.id:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver un simulacro de cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
        bot.register_next_step_handler(msg, simular_cumple, bot)
    


@bot.message_handler(commands=["ahorcado", "hangman"]) 
def cmd_hangman(message):
    '''Iniciando juego del ahorcado'''
    if MY_CHAT_ID == message.chat.id:
        jugar(bot)

#Responder a los mensajes que no son comandos
@bot.message_handler(content_types=["text", "audio", "document", "photo", "sticker", "video", "video_note", 
                                    "voice", "location", "contact", "new_chat_members", "left_chat_member", 
                                    "new_chat_title", "new_chat_photo", "delete_chat_photo", "group_chat_created",
                                    "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                                    "migrate_from_chat_id", "pinned_message"])
def bot_mensajes(message):
    '''Gestiona los mensajes recibidos'''
    if MY_CHAT_ID == message.chat.id:
        if message.text and message.text.startswith("/"):
            bot.send_message(message.chat.id, "Comando no disponible.")
        #else:
            #bot.send_message(message.chat.id, "Yo no respondo, solo felicito cumpleaños.")

def recibir_mensajes():
    '''Bucle infinito que comprueba si hay nuevos mensajes en el bot'''
    bot.infinity_polling()
    
#MAIN
if __name__ == '__main__':
    #file = open ("C:\Users\eleee\Desktop\Bot telegram\DatosCumples.txt", "r")   
    '''
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "da la bienvenida"),
        telebot.types.BotCommand("/iniciar", "da la bienvenida"),
        telebot.types.BotCommand("/help", "muestra lista de comandos disponibles"),
        telebot.types.BotCommand("/ayuda", "muestra lista de comandos disponibles"),
        telebot.types.BotCommand("/add", "añade cumpleaños"),
        telebot.types.BotCommand("/nuevo", "añade cumpleaños"),
        telebot.types.BotCommand("/view", "muestra el cumpleaños del usuario"),
        telebot.types.BotCommand("/ver", "muestra el cumpleaños del usuario"),
        telebot.types.BotCommand("/delete", "borrar un cumpleaños"),
        telebot.types.BotCommand("/borrar", "borrar un cumpleaños"),
        telebot.types.BotCommand("/test", "ejemplo del mensaje de cumpleaños"),
        telebot.types.BotCommand("/probar", "ejemplo del mensaje de cumpleaños")
        telebot.types.BotCommand("/hangman", "jugar al juego del ahorcado")
        telebot.types.BotCommand("/ahorcado", "jugar al juego del ahorcado")
        ])
    '''
    print("Iniciando el bot")
    '''for zone in timezone.available_timezones():
        print(zone)'''
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()
    print("Bot iniciado")
    comprobar_cumples(bot)
    