# coding=utf-8
from config import *                            #Importamos el token y los id de grupo
from fun_birthdays import *                     #Importamos las funciones de los cumpleños
from fun_game import *                          #Importamos el juego del ahorcado
from fun_mod import *                           #Importamos las funciones de moderación
import telebot                                  #Para manejar la API de Telegram
import threading                                #Para el manejo de hilos
import random                                   #Para obtener números aleatorios
from telebot.types import ForceReply            #Para responder a un mensaje
from telebot.types import InlineKeyboardMarkup  #Para crear botones inline
from telebot.types import InlineKeyboardButton  #Para definir botones inline
import pickle                                   #Para serializar objetos para los botones inline
import mysql.connector                          #Para la base de datos

#Instanciamos el bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

#Establecer la conexión con la base de datos
conn = mysql.connector.connect(
    host="nearl-dev.com",
    port="3306",
    user="root",
    password="i#G1zF6402e#",
    database="bot_telegram"
)
cursor = conn.cursor()

#Responder a los comandos
@bot.message_handler(commands=["start", "iniciar"])
def cmd_start(message):
    '''Mensaje de intriducción y presentación del bot'''
    text = ""
    if message.from_user.username == None:
        text += "<b><u>Hola, " + message.from_user.first_name + "!</u></b>\n\n"
        text += "Soy tu bot multifunción, puedo administrar grupos, felicitarte en tu cumpleaños o recordarte el de tus amigos y jugar al ahorcado.\n\nPara saber todo sobre mis comandos introduce /help o /ayuda.\n\nPor favor, es importate para ello que añadas un nombre de usuario en tu perfil, gracias."
    else:
        text += "<b><u>Hola, @" + message.from_user.username + "!</u></b>\n\n"
        text += "Soy tu bot multifunción, puedo administrar grupos, felicitarte en tu cumpleaños o recordarte el de tus amigos y jugar al ahorcado.\n\nPara saber todo sobre mis comandos introduce /help o /ayuda."
    bot.send_message(message.chat.id, text, parse_mode = "html")

@bot.message_handler(commands=["help", "ayuda"])
def cmd_help(message):
    '''Muestra la lista de comandos'''
    text = "<b><u>AYUDA</u></b>\n"
    text += "Estos son los comandos disponibles:\n"
    text += "✰ /start o /iniciar → da la bienvenida\n"
    text += "✰ /help o /ayuda → muestra lista de comandos disponibles\n"
    text += "✰ /register o /registrar → registra un nuevo nombre de usuario en la base de datos\n"
    text += "✰ /config o /configurar → configurar el texto y la foto del mensaje de cumpleaños\n"
    text += "✰ /add o /nuevo → añade cumpleaños\n"
    text += "✰ /view o /ver → muestra el cumpleaños del usuario\n"
    text += "✰ /update o /actualizar → actualiza el cumpleaños del usuario\n"
    text += "✰ /delete o /borrar → borrar un cumpleaños\n"
    text += "✰ /test o /probar → ejemplo del mensaje de cumpleaños\n"
    text += "✰ /warnings o /avisos → muestra los avisos que tiene un usuario\n"
    text += "✰ /unban o /desbanear → comando para administrador, desbanea a un usuario\n"
    text += "✰ /hangman o /ahorcado → jugar al juego del ahorcado\n"
    text += "✰ /ranking o /clasificacion → ver el top 5 del juego del ahorcado\n"
    bot.send_message(message.chat.id, text, parse_mode = "html")

@bot.message_handler(commands=["registrar", "register"])
def cmd_register(message):
    '''Añadir un username por un admin en la base de datos'''
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Este comando es para uso dentro de un grupo.")
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, "¿A que usuario quieres registrar?\nIndica el nombre de usuario con su @.", reply_markup = markup)
            bot.register_next_step_handler(msg, register_user, bot, conn, cursor)
        else:
            if message.from_user.username == None:
                bot.send_message(message.chat.id, "Para usar este comando necesitas añadir un nombre de usuario en tu perfil.")
            else:
                register_user(message, bot, conn, cursor)

@bot.message_handler(commands=["config", "configurar"])
def cmd_config(message):
    '''Configurar la foto y el mensaje de felicitación'''
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "Puedes configurar el mensaje y la foto del mensaje que se mostrará cuando felicite un cumpleaños.\n\n¿Quieres personalizar la foto o el texto?\n\nExcribe 'foto' o 'texto'.", reply_markup = markup)
    bot.register_next_step_handler(msg, config, bot, conn, cursor)

@bot.message_handler(commands=["add", "nuevo"])
def cmd_add(message):
    '''Añadimos un nuevo cumpleaños'''
    input = []
    markup = ForceReply()
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "Al ser un chat privado, actuaré en modo de alertas personales mediante este chat.\n\n¿De quién quieres que guarde el cumpleaños?", reply_markup = markup)
    else:
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres añadir el cumpleaños?\n\nIndica el nombre de usuario con su @.", reply_markup = markup)
    bot.register_next_step_handler(msg, ask_date, bot, input, conn, cursor)

@bot.message_handler(commands=["view", "ver"])
def cmd_view(message):
    '''Muestra cuando es el cumpleaños de un usuario'''
    markup = ForceReply()
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "¿De quién quieres ver el cumpleaños?\n\nDime el nombre con el que lo guardaste.\n\nSi quieres ver la lista completa introduce 'todos'.", reply_markup = markup)
    else:
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver cuándo es su cumpleaños?\n\nIndica el nombre de usuario con su @.\n\nSi quieres ver la lista completa introduce 'todos'.", reply_markup = markup)
    bot.register_next_step_handler(msg, show_birthday, bot, conn, cursor)

@bot.message_handler(commands=["update", "actualizar"])
def cmd_update(message):
    '''Actualizar un cumpleaños'''
    markup = ForceReply()
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "¿De quién quieres actualizar el cumpleaños?\n\nDime el nombre con el que lo guardaste.\n\nPuedes usar el comando /view o /ver e introduciendo 'todos' para ver una lista de los almacenados.", reply_markup = markup)
    else:
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres actualizar el cumpleaños?\n\nIndica el nombre de usuario con su @.\n\nPuedes usar el comando /view o /ver e introduciendo 'todos' para ver una lista de los almacenados.", reply_markup = markup)
    bot.register_next_step_handler(msg, update_birthday, bot, conn, cursor)

@bot.message_handler(commands=["delete", "borrar"])
def cmd_delete(message):
    '''Borrar un cumpleaños'''
    markup = ForceReply()
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "¿De quién quieres borrar el cumpleaños?\n\nDime el nombre con el que lo guardaste.\n\nPuedes usar el comando /view o /ver e introduciendo 'todos' para ver una lista de los almacenados.", reply_markup = markup)
    else:
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres borrar el cumpleaños?\n\nIndica el nombre de usuario con su @.\n\nPuedes usar el comando /view o /ver e introduciendo 'todos' para ver una lista de los almacenados.", reply_markup = markup)
    bot.register_next_step_handler(msg, delete_birthday, bot, conn, cursor)    

@bot.message_handler(commands=["test", "probar"])    
def cmd_test(message):
    '''Prueba el mensaje de cumpleaños'''
    markup = ForceReply()
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "¿De quién quieres ver un simulacro de cumpleaños?\n\nDime el nombre con el que lo guardaste.\n\nPuedes usar el comando /view o /ver e introduciendo 'todos' para ver una lista de los almacenados.", reply_markup = markup)
    else:
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver un simulacro de cumpleaños?\n\nIndica el nombre de usuario con su @.\n\nPuedes usar el comando /view o /ver e introduciendo 'todos' para ver una lista de los almacenados.", reply_markup = markup)
    bot.register_next_step_handler(msg, simulate_birthday, bot, conn, cursor)

@bot.message_handler(commands=["warnings", "avisos"])
def cmd_warnings(message):
    '''Mirar avisos de un usuario'''
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Este comando es para uso dentro de un grupo.")
    else:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver cuántos avisos tiene?\n\nIndica el nombre de usuario con su @.\n\nSi quieres ver la lista completa introduce 'todos'.", reply_markup = markup)
        bot.register_next_step_handler(msg, show_warnings, bot, conn, cursor)

@bot.message_handler(commands=["unban", "desbanear"])
def cmd_unban(message):
    '''Desbanear un usuario'''
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Este comando es para uso dentro de un grupo.")
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, "¿A que usuario quieres desbanear?\n\nIndica el nombre de usuario con su @.\n\nSi quieres ver la lista completa introduce 'todos'.", reply_markup = markup)
            bot.register_next_step_handler(msg, unban_user, bot, conn, cursor)
        else:
            bot.send_message(message.chat.id, "Comando solo disponible para los administradores del grupo.")

@bot.message_handler(commands=["hangman", "ahorcado"])
def cmd_hangman(message):
    '''Iniciando juego del ahorcado'''
    query = "SELECT count(id) FROM hangmanwords"
    cursor.execute(query)
    results = cursor.fetchall()
    idSelectedWord = random.randint(1, results[0][0]+1)
    query = "SELECT * FROM hangmanwords WHERE id = " + str(idSelectedWord)
    cursor.execute(query)
    results = cursor.fetchall()
    selectedWord = results[0][1].lower()
    lives = 6
    inputLetters = ""
    text = ""
    initial_text(bot, message)
    play_hangman(text, lives, selectedWord, inputLetters, bot, message, conn, cursor)

@bot.message_handler(commands=["ranking", "clasificacion"])
def cmd_ranking(message):
    '''Muestra el top 5 del ranking del juego de manera global'''
    query = "SELECT * FROM ranking ORDER BY score DESC LIMIT 5"
    cursor.execute(query)
    results = cursor.fetchall()
    nums = ["🥇", "🥈", "🥉", "4. ","5. "]
    text = "<b><u>RANKING AHORCADO</u></b>" + "\n"
    for i in range(len(results)):
        text += "✰ " + nums[i] + " " + results[i][1] + " → " + str(results[i][2]) + "\n"
    bot.send_message(message.chat.id, text, parse_mode = "html")

#Hacer listados con botones inline
def show_pages(results, id, pag, mid):
    '''Crea o edita un mensaje en la página'''
    markup = InlineKeyboardMarkup()
    b_prev = InlineKeyboardButton("⬅", callback_data = "prev")
    b_next = InlineKeyboardButton("➡", callback_data = "next")
    markup.row(b_prev, b_next)
    start = pag * 10
    end = start + 10
    text = "<i><u><b>Resultados " + str(start + 1) + "-" + str(end) + " de " + str(len(results)) + "</b></u></i>\n\n"
    for i in results[start:end]:
        text += "✰ " + i[0] + " → " + i[1] + "\n"
    if mid != None:
        bot.edit_message_text(text, id, mid, reply_markup = markup, parse_mode = "html")
    else:
        res = bot.send_message(id, text, reply_markup = markup, parse_mode = "html")
        mid = res.message_id
        query = "SELECT * FROM pagesdata where id = " + str(id)
        cursor.execute(query)
        results2 = cursor.fetchall()
        if len(results2) == 0:
            query = "INSERT INTO pagesdata (id, page, list) VALUES (" + str(id) + ", 0, \"" + str(results) + "\")"
            cursor.execute(query)
            conn.commit()
        else:
            query = "UPDATE pagesdata SET page = 0, list = \"" + str(results) + "\" WHERE id = " + str(id)
            cursor.execute(query)
            conn.commit()
    
@bot.callback_query_handler(func=lambda x:True)
def answer_inline_buttons(call):
    cid = call.from_user.id
    mid = call.message.id
    if call.data == "prev":
        #Si estamos en la primera página
        query = "SELECT * FROM pagesdata WHERE id = " + str(cid)
        cursor.execute(query)
        results = cursor.fetchall()
        listAux = results[0][2].replace("[(", "").replace(")]", "").replace("'", "").split("), (")
        list = []
        for i in listAux:
            iaux = i.split(", ")
            list.append(tuple([iaux[0], iaux[1]]))
        if results[0][1] == 0:
            bot.answer_callback_query(call.id, "Ya estás en la primera página")
        else:
            pages = results[0][1] - 1
            query = "UPDATE pagesdata SET page = " + str(pages) + " WHERE id = " + str(cid)
            cursor.execute(query)
            conn.commit()
            show_pages(list, cid, pages, mid)
        return
    elif call.data == "next":
        #Si ya estamos en la última página
        query = "SELECT * FROM pagesdata WHERE id = " + str(cid)
        cursor.execute(query)
        results = cursor.fetchall()
        listAux = results[0][2].replace("[(", "").replace(")]", "").replace("'", "").split("), (")
        list = []
        for i in listAux:
            iaux = i.split(",")
            list.append(tuple([iaux[0], iaux[1]]))
        if results[0][1] * 10 + 10 >= len(list):
            bot.answer_callback_query(call.id, "Ya estás en la última página")
        else:
            pages = results[0][1] + 1
            query = "UPDATE pagesdata SET page = " + str(pages) + " WHERE id = " + str(cid)
            cursor.execute(query)
            conn.commit()
            show_pages(list, cid, pages, mid)
        return

#Responder a los mensajes que no son comandos
@bot.message_handler(content_types=["text"])
def bot_texts(message):
    '''Gestiona los mensajes recibidos'''
    if message.text and message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible.")
    else:
        check_swear_words(message, bot, conn, cursor)

@bot.message_handler(content_types=["new_chat_members"])
def bot_wellcome(message):
    '''Da la bienvenida a los nuevos miembros'''
    text = ""
    newMembers = message.new_chat_members
    for member in newMembers:
        if member.username == "None":
            text += "<b><u>BIENVENID@ " + member.first_name + "</u></b>\n"
            text += "Por favor, añade un nombre de usuario a tu cuenta y avisa a un administrador cuando lo tengas para poder añadir tu cumpleaños, respeta a los miembros del grupo, crea un buen ambiente y modera tu lenguaje."
        else:
            text += "<b><u>BIENVENID@ @" + member.username + "</u></b>\n"
            text += "Por favor, respeta a los miembros del grupo, crea un buen ambiente, modera tu lenguaje y no olvides añadir tu cumpleaños con el comando /nuevo o /add!"
            #LE AÑADIMOS A LA BASE DE DATOS EN LA TABLA DE USUARIOS AUTORIZADOS (USERNAMES)
            user = "@" + member.username
            add_db (user, message.chat.id, conn, cursor)
            #Por si hubiera estado baneado anteriormente
            query = "DELETE FROM bannedusers WHERE id = " + str(member.id)
            cursor.execute(query)
            conn.commit()
        bot.send_message(message.chat.id, text, parse_mode = "html")

@bot.message_handler(content_types=["left_chat_member"])
def bot_goodbye(message):
    '''Despide a los miembros que abandonan el grupo'''
    table = "usernames"
    delete_db (message, table, conn, cursor)
    table = "birthdaydata"
    delete_db (message, table, conn, cursor)
    table = "ranking"
    delete_db (message, table, conn, cursor)

def receive_messages():
    '''Bucle infinito que comprueba si hay nuevos mensajes en el bot'''
    bot.infinity_polling()

#MAIN
if __name__ == "__main__":
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "da la bienvenida"),
        telebot.types.BotCommand("/iniciar", "da la bienvenida"),
        telebot.types.BotCommand("/help", "muestra lista de comandos disponibles"),
        telebot.types.BotCommand("/ayuda", "muestra lista de comandos disponibles"),
        telebot.types.BotCommand("/register", "registra un nuevo nombre de usuario en la base de datos"),
        telebot.types.BotCommand("/registrar", "registra un nuevo nombre de usuario en la base de datos"),
        telebot.types.BotCommand("/config", "configurar el texto y la foto del mensaje de cumpleaños"),
        telebot.types.BotCommand("/configurar", "configurar el texto y la foto del mensaje de cumpleaños"),
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
        telebot.types.BotCommand("/unban", "comando para administrador, desbanea a un usuario"),
        telebot.types.BotCommand("/desbanear", "comando para administrador, desbanea a un usuario"),
        telebot.types.BotCommand("/ranking", "ver el top 5 del juego del ahorcado"),
        telebot.types.BotCommand("/clasificacion", "ver el top 5 del juego del ahorcado"),
        telebot.types.BotCommand("/hangman", "jugar al juego del ahorcado"),
        telebot.types.BotCommand("/ahorcado", "jugar al juego del ahorcado")
        ])
    print("Iniciando el bot")
    bot_thread = threading.Thread(name = "bot_thread", target = receive_messages)
    bot_thread.start()
    print("Bot iniciado")
    startDate = (datetime.now() - timedelta(days = 1)).strftime("%d/%m")
    birthdays_thread = threading.Thread(name = "birthdays_thread", target = verify_birthday, args = (startDate, bot, conn, cursor))
    birthdays_thread.start()
    print("Hilo cumples iniciado")