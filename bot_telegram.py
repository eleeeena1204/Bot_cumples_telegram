# coding=utf-8
from config import *                            #Importamos el token y los id de grupo
from fun_birthdays import *                     #Importamos las funciones de los cumpleños
from fun_game import *                          #Importamos el juego del ahorcado
from fun_mod import *                           #Importamos las funciones de moderación
import telebot                                  #Para manejar la API de Telegram
import threading                                #Para el manejo de hilos
import random                                   #Para obtener números aleatorios
from telebot.types import InlineKeyboardMarkup  #Para crear botones inline
from telebot.types import InlineKeyboardButton  #Para definir botones inline

#Instanciamos el bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

#Responder a los comandos
@bot.message_handler(commands=["start", "iniciar"])
def cmd_start(message):
    '''Mensaje de intriducción y presentación del bot'''
    text = ""
    if message.chat.type == "private":
        if message.from_user.username == None:
            text += "<b><u>Hola, " + message.from_user.first_name + "!</u></b>\n\n"
            text += "Soy tu bot multifunción. Puedo administrar grupos, felicitarte en tu cumpleaños o recordarte el de tus amigos y jugar al ahorcado.\n\nPara saber todo sobre mis comandos, introduce /help o /ayuda.\n\nPor favor, es importate para ello que añadas un nombre de usuario en tu perfil. Gracias."
        else:
            text += "<b><u>Hola, @" + message.from_user.username + "!</u></b>\n\n"
            text += "Soy tu bot multifunción. Puedo administrar grupos, felicitarte en tu cumpleaños o recordarte el de tus amigos y jugar al ahorcado.\n\nPara saber todo sobre mis comandos introduce /help o /ayuda."
    else:
        text += "<b><u>Hola!</u></b>\n\n"
        text += "Soy el bot multifunción de este grupo. Puedo administrar el grupo, felicitar los cumpleaños y jugar al ahorcado.\n\nPara saber todo sobre mis comandos introduce /help o /ayuda.\n\nPor favor, es importate para ello que todos añadan un nombre de usuario en su perfil e introduzcan el comando /register o /registrar para darse de alta en mi base de datos. Gracias."
    bot.send_message(message.chat.id, text, parse_mode = "html")

@bot.message_handler(commands=["help", "ayuda"])
def cmd_help(message):
    '''Muestra la lista de comandos'''
    text = "<b><u>AYUDA</u></b>\n"
    text += "Estos son los comandos disponibles:\n"
    text += "✰ /start o /iniciar → da la bienvenida\n"
    text += "✰ /help o /ayuda → muestra la lista de comandos disponibles\n"
    text += "✰ /register o /registrar → registra un nuevo nombre de usuario en la base de datos\n"
    text += "✰ /config o /configurar → configura el texto y la foto del mensaje de felicitación o de alerta\n"
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
        bot.send_message(message.chat.id, "Este comando solo es para uso dentro de un grupo.")
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "¿A qué usuario quieres registrar?\n\nIndica el nombre de usuario con su @.")
            bot.register_next_step_handler(msg, register_user, bot)
        else:
            if message.from_user.username == None:
                bot.send_message(message.chat.id, "Para usar este comando necesitas añadir un nombre de usuario en tu perfil.")
            else:
                register_user(message, bot)

@bot.message_handler(commands=["config", "configurar"])
def cmd_config(message):
    '''Configurar la foto y el mensaje de felicitación'''
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Este comando solo es para uso dentro de un grupo.")
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "Puedes configurar el mensaje y la foto del mensaje que se mostrará cuando envíe el mensaje de felicitación o de alerta.\n\n¿Quieres personalizar la foto o el texto?\n\nExcribe 'foto' o 'texto'.\n\nPara cancelar, escribe 'salir' o 'exit'.")
            bot.register_next_step_handler(msg, config, bot)
        else:
            bot.send_message(message.chat.id, "Comando solo disponible para los administradores.")

@bot.message_handler(commands=["add", "nuevo"])
def cmd_add(message):
    '''Añadimos un nuevo cumpleaños'''
    input = []
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "Al ser un chat privado, actuaré en modo de alertas personales mediante este chat.\n\n¿De quién quieres que guarde el cumpleaños?")
        bot.register_next_step_handler(msg, ask_date, bot, input)
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "¿De qué usuario quieres añadir el cumpleaños?\n\nIndica el nombre de usuario con su @.")
            bot.register_next_step_handler(msg, ask_date, bot, input)
        else:
            if message.from_user.username == None:
                bot.send_message(message.chat.id, "Para usar este comando necesitas añadir un nombre de usuario en tu perfil.")
            else:
                #El usuario está en el grupo, pero puede que no esté dado de alta en la base de datos porque no haya hecho el /register
                conn = connect_db()
                cursor = conn.cursor()
                query = "SELECT * FROM usernames WHERE name like '@" + message.from_user.username + "' and chatId = " + str(message.chat.id)
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                if len(results) == 0:
                    user = "@" + message.from_user.username
                    add_db (user, message.chat.id)
                conn = connect_db()
                cursor = conn.cursor()
                query = "SELECT * FROM birthdaydata WHERE name like '@" + message.from_user.username + "' and chatId = " + str(message.chat.id)
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                if len(results) == 0:
                    user = "@" + message.from_user.username
                    input.append(user)
                    msg = bot.send_message(message.chat.id, "¿Cuándo es tu cumpleaños?\n\nIndícalo en formato DD/MM.")
                    bot.register_next_step_handler(msg, new_birthday, bot, input)
                else:
                    bot.send_message(message.chat.id, "Ya tienes tu cumpleaños registrado.\n\nPara verlo, usa el comando /view o /ver.\n\nPara cambiarlo, usa el comando /update o /configurar.")

@bot.message_handler(commands=["view", "ver"])
def cmd_view(message):
    '''Muestra cuando es el cumpleaños de un usuario'''
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "¿De quién quieres ver el cumpleaños?\n\nDime el nombre con el que lo guardaste.\n\nSi quieres ver la lista completa, introduce 'todos'.")
    else:
        msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver cuándo es su cumpleaños?\n\nIndica el nombre de usuario con su @.\n\nSi quieres ver la lista completa introduce 'todos'.")
    bot.register_next_step_handler(msg, show_birthday, bot)

@bot.message_handler(commands=["update", "actualizar"])
def cmd_update(message):
    '''Actualizar un cumpleaños'''
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "¿De quién quieres actualizar el cumpleaños?\n\nDime el nombre con el que lo guardaste.")
        bot.register_next_step_handler(msg, update_birthday, bot)
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "¿De qué usuario quieres actualizar el cumpleaños?\n\nIndica el nombre de usuario con su @.")
            bot.register_next_step_handler(msg, update_birthday, bot)
        else:
            if message.from_user.username == None:
                bot.send_message(message.chat.id, "Para usar este comando necesitas añadir un nombre de usuario en tu perfil.")
            else:
                conn = connect_db()
                cursor = conn.cursor()
                query = "SELECT * FROM birthdaydata WHERE name like '@" + message.from_user.username + "' and chatId = " + str(message.chat.id)
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                if len(results) == 0:
                    bot.send_message(message.chat.id, "Para usar este comando necesitas tener tu cumpleaños guardado.\n\nPuedes añadirlo con el comando /add o /nuevo.")
                else:
                    msg = bot.send_message(message.chat.id, "Por favor, introduce la fecha en formato DD/MM.")
                    input = ["@" + message.from_user.username, "existe"]
                    bot.register_next_step_handler(msg, new_birthday, bot, input)

@bot.message_handler(commands=["delete", "borrar"])
def cmd_delete(message):
    '''Borrar un cumpleaños'''
    if message.chat.type == "private":
        msg = bot.send_message(message.chat.id, "¿De quién quieres borrar el cumpleaños?\n\nDime el nombre con el que lo guardaste.")
        bot.register_next_step_handler(msg, delete_birthday, bot)
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "¿De qué usuario quieres borrar el cumpleaños?\n\nIndica el nombre de usuario con su @.")
            bot.register_next_step_handler(msg, delete_birthday, bot)
        else:
            if message.from_user.username == None:
                bot.send_message(message.chat.id, "Para usar este comando necesitas añadir un nombre de usuario en tu perfil.")
            else:
                conn = connect_db()
                cursor = conn.cursor()
                query = "SELECT * FROM birthdaydata WHERE name like '@" + message.from_user.username + "' and chatId = " + str(message.chat.id)
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                if len(results) == 0:
                    bot.send_message(message.chat.id, "No tienes tu cumpleaños guardado, así que no hace falta borrarlo.")
                else:
                    delete_birthday(message, bot)

@bot.message_handler(commands=["test", "probar"])    
def cmd_test(message):
    '''Prueba el mensaje de cumpleaños'''
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Este comando solo es para uso dentro de un grupo.")
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver un simulacro de felicitación?\n\nIndica el nombre de usuario con su @.")
            bot.register_next_step_handler(msg, simulate_birthday, bot)
        else:
            bot.send_message(message.chat.id, "Comando solo disponible para los administradores.")

@bot.message_handler(commands=["warnings", "avisos"])
def cmd_warnings(message):
    '''Mirar avisos de un usuario'''
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Este comando solo es para uso dentro de un grupo.")
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "¿De qué usuario quieres ver cuántos avisos tiene?\n\nIndica el nombre de usuario con su @.\n\nSi no tiene nombre de usuario, introduce su nombre principal.\n\nSi quieres ver la lista completa, introduce 'todos'.")
            bot.register_next_step_handler(msg, show_warnings, bot)
        else:
            bot.send_message(message.chat.id, "Comando solo disponible para los administradores.")

@bot.message_handler(commands=["unban", "desbanear"])
def cmd_unban(message):
    '''Desbanear un usuario'''
    if message.chat.type == "private":
        bot.send_message(message.chat.id, "Este comando solo es para uso dentro de un grupo.")
    else:
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            msg = bot.send_message(message.chat.id, "¿A qué usuario quieres desbanear?\n\nIndica el nombre de usuario con su @.\n\nSi no tiene nombre de usuario, introduce su nombre principal.\n\nSi quieres ver la lista completa, introduce 'todos'.")
            bot.register_next_step_handler(msg, unban_user, bot)
        else:
            bot.send_message(message.chat.id, "Comando solo disponible para los administradores del grupo.")

@bot.message_handler(commands=["hangman", "ahorcado"])
def cmd_hangman(message):
    '''Iniciando juego del ahorcado'''
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT count(id) FROM hangmanwords"
    cursor.execute(query)
    results = cursor.fetchall()
    idSelectedWord = random.randint(1, results[0][0])
    query = "SELECT * FROM hangmanwords WHERE id = " + str(idSelectedWord)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    selectedWord = results[0][1].lower()
    clue = results [0][2]
    lives = 6
    inputLetters = ""
    text = ""
    try:
        initial_text(bot, message)
        play_hangman(text, lives, selectedWord, clue, inputLetters, bot, message)
    except:
        bot.send_message(message.chat.id, "No tengo permiso para iniciar una conversación contigo.\n\nPor favor, escríbeme tu e introduce el comando en nuestro chat para jugar al ahorcado.")

@bot.message_handler(commands=["ranking", "clasificacion"])
def cmd_ranking(message):
    '''Muestra el top 5 del ranking del juego de manera global'''
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT * FROM ranking ORDER BY score DESC LIMIT 5"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    nums = ["🥇", "🥈", "🥉", "4. ","5. "]
    text = "<b><u>RANKING AHORCADO</u></b>" + "\n"
    for i in range(len(results)):
        text += "✰ " + nums[i] + " " + results[i][1] + " → " + str(results[i][2]) + "\n"
    bot.send_message(message.chat.id, text, parse_mode = "html")

#Manejo botones inline
@bot.callback_query_handler(func=lambda x:True)
def answer_inline_buttons(call):
    cid = call.from_user.id
    mid = call.message.id
    if call.data == "prev":
        #Si estamos en la primera página
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM pagesdata WHERE id = " + str(cid)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(results) == 0 or results[0][1] == 0:
            bot.answer_callback_query(call.id, "Ya estás en la primera página")
        else:
            pages = results[0][1] - 1
            conn = connect_db()
            cursor = conn.cursor()
            query = "UPDATE pagesdata SET page = " + str(pages) + " WHERE id = " + str(cid)
            cursor.execute(query)
            conn.commit()
            query = "SELECT * FROM pagesdata WHERE id = " + str(cid)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            show_pages(results, cid, mid, bot)
    elif call.data == "next":
        #Si ya estamos en la última página
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM pagesdata WHERE id = " + str(cid)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        list = []
        if len(results) > 0:
            listAux = results[0][2].replace("[(", "").replace(")]", "").replace("'", "").split("), (")
            for i in listAux:
                iaux = i.split(",")
                list.append(tuple([iaux[0], iaux[1]]))
        if len(results) == 0 or results[0][1] * 10 + 10 >= len(list):
            bot.answer_callback_query(call.id, "Ya estás en la última página")
        else:
            pages = results[0][1] + 1
            conn = connect_db()
            cursor = conn.cursor()
            query = "UPDATE pagesdata SET page = " + str(pages) + " WHERE id = " + str(cid)
            cursor.execute(query)
            conn.commit()
            query = "SELECT * FROM pagesdata WHERE id = " + str(cid)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            show_pages(results, cid, mid, bot)

#Responder a los mensajes que no son comandos
@bot.message_handler(content_types=["text"])
def bot_texts(message):
    '''Gestiona los mensajes recibidos'''
    if message.text and message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible.")
    else:
        check_swear_words(message, bot)

@bot.message_handler(content_types=["new_chat_members"])
def bot_wellcome(message):
    '''Da la bienvenida a los nuevos miembros'''
    text = ""
    newMembers = message.new_chat_members
    for member in newMembers:
        if member.username == None:
            text += "<b><u>BIENVENID@ " + member.first_name + "</u></b>\n"
            text += "Por favor, añade un nombre de usuario a tu cuenta. Cuando lo tengas, introducie el comando /register o /resgistrar para darte de alta.\n\nRespeta a los miembros del grupo, crea un buen ambiente y modera tu lenguaje."
        else:
            text += "<b><u>BIENVENID@ @" + member.username + "</u></b>\n"
            text += "Por favor, respeta a los miembros del grupo, crea un buen ambiente, modera tu lenguaje y no olvides añadir tu cumpleaños con el comando /nuevo o /add!"
            #LE AÑADIMOS A LA BASE DE DATOS EN LA TABLA DE USUARIOS AUTORIZADOS (USERNAMES)
            user = "@" + member.username
            add_db (user, message.chat.id)
            #Por si hubiera estado baneado anteriormente
            conn = connect_db()
            cursor = conn.cursor()
            query = "DELETE FROM bannedusers WHERE id = " + str(member.id)
            cursor.execute(query)
            conn.commit()
            cursor.close()
            conn.close()
        bot.send_message(message.chat.id, text, parse_mode = "html")

@bot.message_handler(content_types=["left_chat_member"])
def bot_goodbye(message):
    '''Despide a los miembros que abandonan el grupo'''
    user = ""
    if message.left_chat_member.username != None:
        user = "@" + message.left_chat_member.username
    else:
        user = message.left_chat_member.first_name
    delete_db (user, "usernames")
    delete_db (user, "birthdaydata")
    delete_db (user, "ranking")

def receive_messages():
    '''Bucle infinito que comprueba si hay nuevos mensajes en el bot'''
    bot.infinity_polling()

#MAIN
if __name__ == "__main__":
    bot.set_my_commands([
        telebot.types.BotCommand("/iniciar", "da la bienvenida"),
        telebot.types.BotCommand("/ayuda", "muestra la lista de comandos disponibles"),
        telebot.types.BotCommand("/registrar", "registra un nuevo nombre de usuario en la base de datos"),
        telebot.types.BotCommand("/configurar", "configurar el texto y la foto del mensaje de felicitación o de alerta"),
        telebot.types.BotCommand("/nuevo", "añade cumpleaños"),
        telebot.types.BotCommand("/ver", "muestra el cumpleaños del usuario"),
        telebot.types.BotCommand("/actualizar", "actualiza el cumpleaños del usuario"),
        telebot.types.BotCommand("/borrar", "borrar un cumpleaños"),
        telebot.types.BotCommand("/probar", "ejemplo del mensaje de cumpleaños"),
        telebot.types.BotCommand("/avisos", "muestra los avisos que tiene un usuario"),
        telebot.types.BotCommand("/desbanear", "comando para administrador, desbanea a un usuario"),
        telebot.types.BotCommand("/clasificacion", "ver el top 5 del juego del ahorcado"),
        telebot.types.BotCommand("/ahorcado", "jugar al juego del ahorcado")
        ])
    bot_thread = threading.Thread(name = "bot_thread", target = receive_messages)
    bot_thread.start()
    print("Bot iniciado")
    startDate = (datetime.now() - timedelta(days = 1)).strftime("%d/%m")
    birthdays_thread = threading.Thread(name = "birthdays_thread", target = verify_birthday, args = (startDate, bot))
    birthdays_thread.start()
    print("Hilo cumples iniciado")