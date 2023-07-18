# coding=utf-8
from config import *                        #Importamos el token y los id de grupo
from bot_telegram import *                  #Necesitaremos las funciones del listado con botones
from datetime import *                      #Para el manejo de horas

#Función para registrar un usuario --------------------------------------------------------------------------------------------------------
def register_user(message, bot, conn, cursor):
    '''Añadimos el user en la base de datos'''
    if message.content_type == "text":
        if message.text != "exit" and message.text != "salir":
            if message.text.startswith("/"):
                add_db("@" + message.from_user.username, message.chat.id, conn, cursor)
            else:
                if message.text.startswith("@"):
                    if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
                        query = "SELECT * FROM usernames WHERE name like '" + message.text + "'"
                        cursor.execute(query)
                        results = cursor.fetchall()
                        if len(results) == 0:
                            add_db(message.text, message.chat.id, conn, cursor)
                            bot.send_message(message.chat.id, "Usuario registrado.")
                        else:
                            bot.send_message(message.chat.id, "Este usuario ya está registrado.")
                    else:
                        markup = ForceReply()
                        msg = bot.send_message(message.chat.id, "Acción disponible para los administradores del grupo, por favor no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.", reply_markup = markup)
                        bot.register_next_step_handler(msg, register_user, bot, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, "Por favor, introduce el nombre de usuario que empieza con @ o escribe 'salir' o 'exit' para cancelar.", reply_markup = markup)
                    bot.register_next_step_handler(msg, register_user, bot, conn, cursor)
        else:
            bot.send_message(message.chat.id, "Se ha cancelado el registro del usuario.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función para añadir usuarios a la base de datos en la bienvenida --------------------------------------------------------------------------------------------------------
def add_db (member, chatId, conn, cursor):
    '''Añadimos al usuario en la base de datos de username'''
    query = "SELECT MAX(id) AS ultimo_id FROM usernames"
    cursor.execute(query)
    results = cursor.fetchall()
    id = 1
    print(results)
    if results[0][0] != None:
        id = results[0][0]+1
    query = "INSERT INTO usernames (id, name, chatId) VALUES (" + str(id) + ", '" + member + "', " + str(chatId) + ")"
    cursor.execute(query)
    conn.commit()

#Función para eliminar usuarios de la base de datos cuando salen del grupo --------------------------------------------------------------------------------------------------------
def delete_db (message, table, conn, cursor):
    '''Eliminamos la aparición del usuario de la tabla elegida en la base de datos'''
    query = "DELETE FROM " + table + " WHERE name like '@" + message.left_chat_member.username + "'"
    cursor.execute(query)
    conn.commit()

#Función para mostrar los avisos de moderacion de un usuario --------------------------------------------------------------------------------------------------------
def show_warnings(message, bot, conn, cursor):
    '''Mostramos los avisos que tiene un usuario'''
    if message.content_type == 'text':
        if message.text.lower() == "todos":
            query = "SELECT name, warnings FROM warnedusers WHERE chatId = " + str(message.chat.id)
            cursor.execute(query)
            results =  cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "No hay usuarios con advertencias.")
            else:
                show_pages(results, message.chat.id, 0, None)
        else:
            user = message.text
            query = "SELECT * FROM warnedusers WHERE name like '" + user + "'"
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "El usuario introducido no tiene ningún aviso.")
            else:
                bot.send_message(message.chat.id, "El usuario " + user + " tiene " + str(results[0][2]) + " avisos.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función para comprobar si en el mensaje hay palabrotas --------------------------------------------------------------------------------------------------------
def check_swear_words(message, bot, conn, cursor):
    '''Comprobamos que en el texto no haya palabrotas y baneamos en caso de encontra alguna'''
    isSwearWord = False
    mensaje = message.text.lower().split(" ")
    for word in mensaje:
        query = "SELECT * FROM swearwords WHERE word like '" + word + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) != 0:
            isSwearWord = True
    if isSwearWord:
        bot.delete_message(message.chat.id, message.message_id)
        if (bot.get_chat_member(message.chat.id, message.from_user.id).status not in ["creator", "administrator"]) or (message.chat.id != MY_CHAT_ID):
            if message.chat.type == "private":
                bot.send_message(message.chat.id, "Estoy programado para eliminar mensajes que contengan ciertas palabras ofensivas.")
            else:
                query = "SELECT * FROM warnedusers WHERE id =" + str(message.from_user.id)
                cursor.execute(query)
                results = cursor.fetchall()
                if len(results) == 0:
                    query = "INSERT INTO warnedusers (id, name, warnings, chatId) VALUES (" + str(message.from_user.id) + ", '@" + message.from_user.username + "', 1, " + str(message.chat.id) + ")"
                    cursor.execute(query)
                    conn.commit()
                    bot.send_message(message.chat.id, "Modera tu lenguaje, @" + message.from_user.username + ", es tu primer aviso, al tercero serás baneado del grupo durante 24 horas.")
                else:
                    if results[0][2] == 2:
                        #Baneado del grupo
                        banEnd = datetime.now() + timedelta(minutes = 1) #ESTO SERÁN 24H
                        query = "INSERT INTO bannedusers (id, name, banend, chatId) VALUES (" + str(message.from_user.id) + ", '@" + message.from_user.username + "', '" + str(banEnd) + "', " + str(message.chat.id) + ")"
                        cursor.execute(query)
                        conn.commit()
                        query = "DELETE FROM warnedusers WHERE id = " + str(message.from_user.id)
                        cursor.execute(query)
                        conn.commit()
                        bot.send_message(message.chat.id, "El usuario @" + message.from_user.username + " ha sido baneado del grupo hasta " + str(banEnd) + ".")
                        bot.ban_chat_member(message.chat.id, message.from_user.id, until_date = banEnd)
                    else:
                        query = "UPDATE warnedusers SET warnings = " + str(results[0][2]+1) + " WHERE id = " + str(results[0][0])
                        cursor.execute(query)
                        conn.commit()
                        bot.send_message(message.chat.id, "Modera tu lenguaje, @" + message.from_user.username + ", es tu segundo aviso, al tercero serás baneado del grupo durante 24 horas.")

#Función para desbanear un usuario --------------------------------------------------------------------------------------------------------
def unban_user(message, bot, conn, cursor):
    '''Desbanear un usuario'''
    if message.content_type == 'text':
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
                bot.send_message(message.chat.id, "No hay usuarios baneados.")
            else:
                show_pages(results, message.chat.id, 0, None)
        else:
            query = "SELECT * FROM bannedusers WHERE name like '" + message.text + "'"
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "Este usuario no está baneado, puede invitarle al grupo.")
            else:
                if datetime.now() > datetime.strptime(results[0][2], '%Y-%m-%d %H:%M:%S.%f'):
                    #Ya pasó el tiempo de baneo
                    query = "DELETE FROM bannedusers WHERE name like '" + message.text + "'"
                    cursor.execute(query)
                    conn.commit()
                    bot.send_message(message.chat.id, "Este usuario no está baneado, puede invitarle al grupo.")
                else:
                    bot.unban_chat_member(message.chat.id, results[0][0])
                    query = "DELETE FROM bannedusers WHERE name like '" + message.text + "'"
                    cursor.execute(query)
                    conn.commit()
                    bot.send_message(message.chat.id, "El usuario " + message.text + " ya no está baneado, puede invitarle al grupo de nuevo.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")
