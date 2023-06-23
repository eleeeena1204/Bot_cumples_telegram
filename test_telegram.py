from config import *                            #Importamos el token y los id de grupo
from fun_cumples import *                       #Importamos las funciones de los cumpleños
from juego import *                             #Importamos el juego del ahorcado
from fun_mod import *                           #Importamos las funciones de moderación
import telebot                                  #Para manejar la API de Telegram
import threading                                #Para el manejo de hilos
#from telebot.types import ReplyKeyboardMarkup   #botones y demás
from telebot.types import ForceReply            #Para responder a un mensaje
#import os   #para borrar lineas en un fichero
#from datetime import datetime   #para el manejo de horas
#from pytz import timezone     #para las franjas horarias
import mysql.connector                          #Para la base de datos

#Instanciamos el bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Establecer la conexión con la base de datos
conn = mysql.connector.connect(
    host='containers-us-west-172.railway.app',
    port='5666',
    user='root',
    password='VX6UWVT2SaQkPGGM8yid',
    database='railway'
)
cursor = conn.cursor()

#Responder a los comandos
@bot.message_handler(commands=["start", "iniciar"])
def cmd_start(message):
    '''Da la bienvenida al usuario del bot'''
    if MY_CHAT_ID == message.chat.id:
        text = '<b><u>HOLA!</u></b>' + '\n'
        text += 'Soy tu bot de cumpleaños, añade el tuyo para felicitarte.'        
        bot.send_message(message.chat.id, text, parse_mode='html')
    
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
        text += '✰ /update o /actualizar → actualiza el cumpleaños del usuario' + '\n'
        text += '✰ /delete o /borrar → borrar un cumpleaños' + '\n'
        text += '✰ /test o /probar → ejemplo del mensaje de cumpleaños' + '\n'
        text += '✰ /warnings o /avisos → muestra los avisos que tiene un usuario' + '\n'
        text += '✰ /hangman o /ahorcado → jugar al juego del ahorcado' + '\n'
        bot.send_message(message.chat.id, text, parse_mode='html')

@bot.message_handler(commands=["add", "nuevo"])    
def cmd_add(message):
    '''Añadimos un nuevo cumpleaños'''
    entrada = []
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿De qué usuario quieres añadir el cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
    bot.register_next_step_handler(msg, preguntar_zona_horaria, bot, entrada, conn, cursor)   
    
@bot.message_handler(commands=["view", "ver"])    
def cmd_view(message):
    '''Muestra cuando es el cumpleaños de un usuario'''
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver cuándo es su cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
    bot.register_next_step_handler(msg, mostrar_cumple, bot, conn, cursor)    

@bot.message_handler(commands=["update", "actualizar"])
def cmd_update(message):
    '''Actualizar un cumpleaños'''
    markup = ForceReply()
    msg =bot.send_message(message.chat.id, "¿De qué usuario quieres actualizar el cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
    bot.register_next_step_handler(msg, actualizar_cumple, bot, conn, cursor)    

@bot.message_handler(commands=["delete", "borrar"])    
def cmd_delete(message):
    '''Borrar un cumpleaños'''
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿De qué usuario quieres borrar el cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
    bot.register_next_step_handler(msg, borrar_cumple, bot, conn, cursor)    

@bot.message_handler(commands=["test", "probar"])    
def cmd_test(message):
    '''Prueba el mensaje de cumpleaños'''
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver un simulacro de cumpleaños?\nIndica el nombre con su @.", reply_markup=markup)
    bot.register_next_step_handler(msg, simular_cumple, bot, conn, cursor)
    
@bot.message_handler(commands=["warnings", "avisos"])
def cmd_warnings(message):
    '''Mirar avisos de un usuario'''
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver cuántos avisos tiene?", reply_markup=markup)
    bot.register_next_step_handler(msg, mostrar_avisos, bot, conn, cursor) 
    
@bot.message_handler(commands=["ahorcado", "hangman"]) 
def cmd_hangman(message):
    '''Iniciando juego del ahorcado'''
    jugar(bot, conn, cursor)

#Responder a los mensajes que no son comandos
'''@bot.message_handler(content_types=["text", "audio", "document", "photo", "sticker", "video", "video_note", 
                                    "voice", "location", "contact", "new_chat_members", "left_chat_member", 
                                    "new_chat_title", "new_chat_photo", "delete_chat_photo", "group_chat_created",
                                    "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                                    "migrate_from_chat_id", "pinned_message"])'''
@bot.message_handler(content_types=["text"])                                    
def bot_mensajes(message):
    '''Gestiona los mensajes recibidos'''
    if message.text and message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible.")
    else:
        comprobar_palabrota(message, bot, conn, cursor)

@bot.message_handler(content_types=["new_chat_members"])
def bot_wellcome(message):
    '''Da la bienvenida a los nuevos miembros'''
    text = ''
    if message.new_chat_members[0].username == 'None':
        text += '<b><u>BIENVENID@ ' + message.new_chat_members[0].first_name + '</u></b>' + '\n'
        text += 'Por favor, añade un nombre de usuario a tu cuenta y avisa a un administrador cuando lo tengas para poder añadir tu cumpleaños en el bot, respeta a los miembros del grupo, crea un buen ambiente y modera tu lenguaje'
    else:
        text += '<b><u>BIENVENID@ @' + message.new_chat_members[0].username + '</u></b>' + '\n'
        text += 'Por favor, respeta a los miembros del grupo, crea un buen ambiente, modera tu lenguaje y no olvides añadir tu cumpleaños en el bot con el comando /nuevo o /add!'   
        #LE AÑADIMOS A LA BASE DE DATOS EN LA TABLA DE USUARIOS AUTORIZADOS (USERNAME)
        add_db (message, conn, cursor)
    bot.send_message(message.chat.id, text, parse_mode='html')
    
@bot.message_handler(content_types=["left_chat_member"])
def bot_goodbye(message):
    '''Despide a los miembros que abandonan el grupo''' 
    #NO MANDAMOS MENSAJE PORQUE NO LO VAN A LEER PERO SI QUE LES BORRAMOS DE LA BASE DE DATOS
    tabla = 'username'
    delete_db (message, tabla, conn, cursor)
    tabla = 'bannedusers'
    delete_db (message, tabla, conn, cursor)
    tabla = 'birthdaydata'
    delete_db (message, tabla, conn, cursor)

def recibir_mensajes():
    '''Bucle infinito que comprueba si hay nuevos mensajes en el bot'''
    bot.infinity_polling()
    
#MAIN
if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "da la bienvenida"),
        telebot.types.BotCommand("/iniciar", "da la bienvenida"),
        telebot.types.BotCommand("/help", "muestra lista de comandos disponibles"),
        telebot.types.BotCommand("/ayuda", "muestra lista de comandos disponibles"),
        telebot.types.BotCommand("/add", "añade cumpleaños"),
        telebot.types.BotCommand("/nuevo", "añade cumpleaños"),
        telebot.types.BotCommand("/view", "muestra el cumpleaños del usuario"),
        telebot.types.BotCommand("/ver", "muestra el cumpleaños del usuario"),
        telebot.types.BotCommand("/update", "actualiza el cumpleaños del usuario"),
        telebot.types.BotCommand("/actualizar", "actualiza el cumpleaños del usuario"),
        telebot.types.BotCommand("/delete", "borrar un cumpleaños"),
        telebot.types.BotCommand("/borrar", "borrar un cumpleaños"),
        telebot.types.BotCommand("/test", "ejemplo del mensaje de cumpleaños"),
        telebot.types.BotCommand("/probar", "ejemplo del mensaje de cumpleaños"),
        telebot.types.BotCommand("/warnings", "muestra los avisos que tiene un usuario"),
        telebot.types.BotCommand("/avisos", "muestra los avisos que tiene un usuario"),
        telebot.types.BotCommand("/hangman", "jugar al juego del ahorcado"),
        telebot.types.BotCommand("/ahorcado", "jugar al juego del ahorcado")
        ])
    print("Iniciando el bot")
    '''for zone in timezone.available_timezones():
        print(zone)'''
    hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    hilo_bot.start()
    print("Bot iniciado")
    comprobar_cumples(bot, conn, cursor)    