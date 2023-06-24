#Función para mostrar los avisos de moderacion de un usuario -------------------------------------------------------------------------------------------------------- 
def mostrar_avisos(message, bot, conn, cursor):
    '''Mostramos los avisos que tiene un usuario'''
    user = message.text
    query = "SELECT * FROM warnedusers WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(message.chat.id, "El usuario introducido no tiene ningún aviso.")
    else:
        bot.send_message(message.chat.id, "El usuario " + user + " tiene " + str(results[0][2]) + " avisos.")

#Función para eliminar usuarios de la base de datos cuando salen del grupo -------------------------------------------------------------------------------------------------------- 
def delete_db (message, tabla, conn, cursor):
    '''Eliminamos la aparición del usuario de la tabla elegida en la base de datos'''
    query = "DELETE FROM " + tabla + " WHERE name like '" + message.left_chat_member.username + "'"
    cursor.execute(query)
    conn.commit() #Importante para que se guarden los cambios de la consulta.
    
#Función para añadir usuarios a la base de datos en la bienvenida -------------------------------------------------------------------------------------------------------- 
def add_db (member, conn, cursor):
    '''Añadimos al usuario en la base de datos de username'''       
    query = "SELECT MAX(id) AS ultimo_id FROM usernames"
    cursor.execute(query)
    results = cursor.fetchall()
    id = results[0][0]+1
    query = "INSERT INTO usernames (id, name) VALUES (" + str(id) + ", '@" + member.username + "')"
    cursor.execute(query)
    conn.commit() #Importante para que se guarden los cambios de la consulta.

#Función para comprobar si en el mensaje hay palabrotas -------------------------------------------------------------------------------------------------------- 
def comprobar_palabrota(message, bot, conn, cursor):
    '''Comprobamos que en el texto no haya palabrotas y baneamos en caso de encontra alguna'''
    haypalabrota = False
    mensaje = message.text.lower().split(" ")
    for palabra in mensaje:
        query = "SELECT * FROM badwords WHERE word like '" + palabra + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) != 0:
            haypalabrota = True
    if haypalabrota:
        bot.delete_message(message.chat.id, message.message_id)
        query = "SELECT * FROM warnedusers WHERE name like '@" + message.from_user.username + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            query = "SELECT MAX(id) AS ultimo_id FROM warnedusers"
            cursor.execute(query)
            results = cursor.fetchall()
            id = 0
            if results[0][0] == 'None':
                id = results[0][0]+1
            query = "INSERT INTO warnedusers (id, name, warnings) VALUES (" + str(id) + ", '@" + message.from_user.username + "', 1)"
            cursor.execute(query)
            conn.commit() #Importante para que se guarden los cambios de la consulta.
            bot.send_message(message.chat.id, "Modera tu lenguaje, es tu primer aviso, al tercero serás baneado del grupo durante 24 horas.", parse_mode='html')
        else:
            if results[0][2] == 2:
                #Baneado del grupo
                fin_ban = datetime.now() + timedelta(hours = 24)
                if bot.get_chat_member(message.chat.id, message.from_user.id).status not in ["creator", "administrator"]:
                    bot.ban_chat_member(message.chat.id, message.from_user.id, until_date = fin_ban)
                bot.send_message(message.chat.id, "El usuario @" + message.from_user.username + " ha sido baneado del grupo hasta " + fin_ban, parse_mode='html')                
                query = "INSERT INTO bannedusers (id, name) VALUES (" + message.from_user.id + ", '@" + message.from_user.username + "')"
                cursor.execute(query)
                conn.commit()
                query = "DELETE FROM warnedusers WHERE name like '@" + message.from_user.username + "'"
                cursor.execute(query)
                conn.commit()
            else:
                query = "UPDATE warnedusers SET warnings = " + str(results[0][2]+1) + " WHERE name = '" + results[0][1] + "'"
                cursor.execute(query)
                conn.commit()
                bot.send_message(message.chat.id, "Modera tu lenguaje, es tu segundo aviso, al tercero serás baneado del grupo durante 24 horas.", parse_mode='html')
 
#Función para desbanear un usuario --------------------------------------------------------------------------------------------------------
def unban_user(message, bot, conn, cursor):
    '''Desbanear un usuario'''
    query = "SELECT * FROM bannedusers WHERE name like '" + message.text + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(message.chat.id, "Este usuario no está baneado, puede invitarle al grupo.", parse_mode='html')
    else:
        bot.unban_chat_member(message.chat.id, results[0][0])
        query = "DELETE FROM bannedusers WHERE name like '" + message.text + "'"
        cursor.execute(query)
        conn.commit()
        bot.send_message(message.chat.id, "El usuario " + message.text + " ya no está baneado, puede invitarle al grupo de nuevo.", parse_mode='html')