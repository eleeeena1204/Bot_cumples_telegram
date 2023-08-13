# coding=utf-8
from config import *                        #Importamos el token y los id de grupo
from datetime import *                      #Para el manejo de horas
from telebot.types import InlineKeyboardMarkup  #Para crear botones inline
from telebot.types import InlineKeyboardButton  #Para definir botones inline
import mysql.connector                          #Para la base de datos

#Establecer la conexión con la base de datos --------------------------------------------------------------------------------------------------------
def connect_db():
    '''Abrimos conexión con la base de datos'''
    conn = mysql.connector.connect(
        host="NOMBRE DEL HOST",
        port="PUERTO DEL HOST",
        user="NOMBRE DEL USUARIO",
        password="CONTRASEÑA",
        database="NOMBRE DE LA BASE DE DATOS"
    )
    return conn

#Función /register o /registrar --------------------------------------------------------------------------------------------------------
def register_user(message, bot):
    '''Añadimos el user en la base de datos'''
    if message.content_type == "text":
        if message.text.startswith("/"):
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT * FROM usernames WHERE name like '@" + message.from_user.username + "' and chatId = " + str(message.chat.id)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            if len(results) == 0:
                add_db("@" + message.from_user.username, message.chat.id)
                bot.send_message(message.chat.id, "Usuario registrado.")
            else:
                bot.send_message(message.chat.id, "Ya estabas registrado.") 
        else:
            if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
                if message.text.lower() != "exit" and message.text.lower() != "salir":
                    if message.text.startswith("@"):
                        conn = connect_db()
                        cursor = conn.cursor()
                        query = "SELECT * FROM usernames WHERE name like '" + message.text + "' and chatId = " + str(message.chat.id)
                        cursor.execute(query)
                        results = cursor.fetchall()
                        cursor.close()
                        conn.close()
                        if len(results) == 0:
                            add_db(message.text, message.chat.id)
                            bot.send_message(message.chat.id, "Usuario registrado.")
                        else:
                            bot.send_message(message.chat.id, "Este usuario ya está registrado. Si quieres, vuelve a intentarlo escribiendo otra vez el comando /register o /registrar.")
                    else:
                        msg = bot.send_message(message.chat.id, "Por favor, introduce el nombre de usuario con su @ o escribe 'salir' o 'exit' para cancelar.")
                        bot.register_next_step_handler(msg, register_user, bot)
                else:
                    bot.send_message(message.chat.id, "Se ha cancelado el registro del usuario.")
            else:
                msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
                bot.register_next_step_handler(msg, register_user, bot)
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función para añadir usuarios a la base de datos en la bienvenida --------------------------------------------------------------------------------------------------------
def add_db (member, chatId):
    '''Añadimos al usuario en la base de datos de username'''
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT MAX(id) AS ultimo_id FROM usernames"
    cursor.execute(query)
    results = cursor.fetchall()
    id = 1
    if results[0][0] != None:
        id = results[0][0]+1
    query = "INSERT INTO usernames (id, name, chatId) VALUES (" + str(id) + ", '" + member + "', " + str(chatId) + ")"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

#Función para eliminar usuarios de la base de datos cuando salen del grupo --------------------------------------------------------------------------------------------------------
def delete_db (user, table):
    '''Eliminamos la aparición del usuario de la tabla elegida en la base de datos'''
    conn = connect_db()
    cursor = conn.cursor()
    query = "DELETE FROM " + table + " WHERE name like '" + user + "'"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

#Función /warnings o /avisos --------------------------------------------------------------------------------------------------------
def show_warnings(message, bot):
    '''Mostramos los avisos que tiene un usuario'''
    if message.content_type == 'text':
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            if message.text.lower() != "exit" and message.text.lower() != "salir":
                conn = connect_db()
                cursor = conn.cursor()
                if message.text.lower() == "todos":
                    query = "SELECT name, warnings FROM warnedusers WHERE chatId = " + str(message.chat.id)
                    cursor.execute(query)
                    results =  cursor.fetchall()
                    if len(results) == 0:
                        bot.send_message(message.chat.id, "No hay ningún usuario con avisos.")
                    else:
                        query = "SELECT * FROM pagesdata where id = " + str(message.chat.id)
                        cursor.execute(query)
                        results2 = cursor.fetchall()
                        if len(results2) == 0:
                            query = "INSERT INTO pagesdata (id, page, list) VALUES (" + str(message.chat.id) + ", 0, \"" + str(results) + "\")"
                            cursor.execute(query)
                            conn.commit()
                        else:
                            query = "UPDATE pagesdata SET page = 0, list = \"" + str(results) + "\" WHERE id = " + str(message.chat.id)
                            cursor.execute(query)
                            conn.commit()
                        query = "SELECT * FROM pagesdata where id = " + str(message.chat.id)
                        cursor.execute(query)
                        results2 = cursor.fetchall()
                        cursor.close()
                        conn.close()
                        show_pages(results2, message.chat.id, None, bot)
                else:
                    user = message.text
                    query = "SELECT * FROM warnedusers WHERE name like '" + user + "'"
                    cursor.execute(query)
                    results = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    if len(results) == 0:
                        bot.send_message(message.chat.id, "El usuario introducido no tiene ningún aviso.")
                    else:
                        bot.send_message(message.chat.id, "El usuario " + user + " tiene " + str(results[0][2]) + " avisos.")
            else:
                bot.send_message(message.chat.id, "Se ha cancelado la visualización de avisos.")
        else:
            msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
            bot.register_next_step_handler(msg, show_warnings, bot)
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función para comprobar si en el mensaje hay palabrotas --------------------------------------------------------------------------------------------------------
def check_swear_words(message, bot):
    '''Comprobamos que en el texto no haya palabrotas y baneamos en caso de encontra alguna'''
    isSwearWord = False
    mensaje = message.text.lower().split(" ")
    conn = connect_db()
    cursor = conn.cursor()
    for word in mensaje:
        query = "SELECT * FROM swearwords WHERE word like '" + word + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) != 0:
            isSwearWord = True
    if isSwearWord:
        bot.delete_message(message.chat.id, message.message_id)
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status not in ["creator", "administrator"]) or (message.from_user.id != MY_CHAT_ID):
            if message.chat.type == "private":
                bot.send_message(message.chat.id, "Estoy programado para eliminar mensajes que contengan ciertas palabras ofensivas.")
            else:
                query = "SELECT * FROM warnedusers WHERE id =" + str(message.from_user.id)
                cursor.execute(query)
                results = cursor.fetchall()
                user = ""
                if message.from_user.username == None:
                    user = message.from_user.first_name
                else:
                    user = "@" + message.from_user.username
                if len(results) == 0:
                    query = "INSERT INTO warnedusers (id, name, warnings, chatId) VALUES (" + str(message.from_user.id) + ", '" + user + "', 1, " + str(message.chat.id) + ")"
                    cursor.execute(query)
                    conn.commit()
                    bot.send_message(message.chat.id, "Modera tu lenguaje, " + user + ".\n\nEs tu primer aviso.\n\nAl tercero serás baneado del grupo durante 24 horas.")
                else:
                    if results[0][2] == 2:
                        #Baneado del grupo
                        banEnd = datetime.now() + timedelta(minutes = 1) #ESTO SERÁN 24H
                        query = "INSERT INTO bannedusers (id, name, banend, chatId) VALUES (" + str(message.from_user.id) + ", '" + user + "', '" + str(banEnd) + "', " + str(message.chat.id) + ")"
                        cursor.execute(query)
                        conn.commit()
                        query = "DELETE FROM warnedusers WHERE id = " + str(message.from_user.id)
                        cursor.execute(query)
                        conn.commit()
                        bot.send_message(message.chat.id, "El usuario " + user + " ha sido baneado del grupo hasta " + str(banEnd) + ".")
                        bot.ban_chat_member(message.chat.id, message.from_user.id, until_date = banEnd)
                    else:
                        query = "UPDATE warnedusers SET warnings = " + str(results[0][2]+1) + " WHERE id = " + str(results[0][0])
                        cursor.execute(query)
                        conn.commit()
                        bot.send_message(message.chat.id, "Modera tu lenguaje, " + user + ".\n\nEs tu segundo aviso.\n\nAl tercero serás baneado del grupo durante 24 horas.")
    cursor.close()
    conn.close()

#Función /unban o /desbanear --------------------------------------------------------------------------------------------------------
def unban_user(message, bot):
    '''Desbanear un usuario'''
    if message.content_type == 'text':
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            if message.text.lower() != "exit" and message.text.lower() != "salir":
                conn = connect_db()
                cursor = conn.cursor()
                if message.text.lower() == "todos":
                    query = "SELECT name, banend FROM bannedusers WHERE chatId = " + str(message.chat.id)
                    cursor.execute(query)
                    results =  cursor.fetchall()
                    for i in results:
                        if datetime.now() > datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f'):
                            #Ya pasó el tiempo de baneo
                            query = "DELETE FROM bannedusers WHERE name like '" + i[0] + "'"
                            cursor.execute(query)
                            conn.commit()
                            results.remove(i)
                    if len(results) == 0:
                        bot.send_message(message.chat.id, "No hay ningún usuario baneado.")
                    else:
                        query = "SELECT * FROM pagesdata where id = " + str(message.chat.id)
                        cursor.execute(query)
                        results2 = cursor.fetchall()
                        if len(results2) == 0:
                            query = "INSERT INTO pagesdata (id, page, list) VALUES (" + str(message.chat.id) + ", 0, \"" + str(results) + "\")"
                            cursor.execute(query)
                            conn.commit()
                        else:
                            query = "UPDATE pagesdata SET page = 0, list = \"" + str(results) + "\" WHERE id = " + str(message.chat.id)
                            cursor.execute(query)
                            conn.commit()
                        query = "SELECT * FROM pagesdata where id = " + str(message.chat.id)
                        cursor.execute(query)
                        results2 = cursor.fetchall()
                        show_pages(results2, message.chat.id, None, bot)
                else:
                    query = "SELECT * FROM bannedusers WHERE name like '" + message.text + "'"
                    cursor.execute(query)
                    results = cursor.fetchall()
                    if len(results) == 0:
                        bot.send_message(message.chat.id, "Este usuario no está baneado.\n\nPuedes invitarlo al grupo.")
                    else:
                        bot.unban_chat_member(message.chat.id, results[0][0])
                        query = "DELETE FROM bannedusers WHERE name like '" + message.text + "'"
                        cursor.execute(query)
                        conn.commit()
                        bot.send_message(message.chat.id, "El usuario " + message.text + " ya no está baneado.\n\nPuedes invitarlo al grupo de nuevo.")
                cursor.close()
                conn.close()
            else:
                bot.send_message(message.chat.id, "Se ha cancelado el desbaneo del usuario.")
        else:
            msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
            bot.register_next_step_handler(msg, unban_user, bot)
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Hacer listados con botones inline
def show_pages(results, id, mid, bot):
    '''Crea o edita un mensaje en la página'''
    markup = InlineKeyboardMarkup()
    b_prev = InlineKeyboardButton("⬅", callback_data = "prev")
    b_next = InlineKeyboardButton("➡", callback_data = "next")
    markup.row(b_prev, b_next)
    start = int(results[0][1]) * 10
    end = start + 10
    listAux = results[0][2].replace("[(", "").replace(")]", "").replace("'", "").split("), (")
    list = []
    for i in listAux:
        iaux = i.split(", ")
        list.append(tuple([iaux[0], iaux[1]]))
    text = "<i><u><b>Resultados " + str(start + 1) + "-" + str(end) + " de " + str(len(list)) + "</b></u></i>\n\n"
    for i in list[start:end]:
        text += "✰ " + i[0] + " → " + i[1] + "\n"
    if mid != None:
        bot.edit_message_text(text, id, mid, reply_markup = markup, parse_mode = "html")
    else:
        bot.send_message(id, text, reply_markup = markup, parse_mode = "html")
