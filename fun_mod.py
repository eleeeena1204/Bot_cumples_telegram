#Función para mostrar los avisos de moderacion de un usuario -------------------------------------------------------------------------------------------------------- 
def mostrar_avisos(message, bot, conn, cursor):
    '''Mostramos los avisos que tiene un usuario'''
    user = message.text
    query = "SELECT * FROM bannedusers WHERE name like '@" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(message.chat.id, "El usuario introducido no tiene ningún aviso.")
    else:
        bot.send_message(message.chat.id, "El usuario introducido tiene " + str(results[0][2]) + " avisos.")

#Función para eliminar usuarios de la base de datos -------------------------------------------------------------------------------------------------------- 
def delete_db (message, tabla, conn, cursor):
    '''Eliminamos la aparición del usuario de la tabla elegida en la base de datos'''
    query = "DELETE FROM " + tabla + " WHERE name like '@" + message.left_chat_member.username + "'"
    cursor.execute(query)
    conn.commit() #Importante para que se guarden los cambios de la consulta.
    
#Función para añadir usuarios a la base de datos en la bienvenida -------------------------------------------------------------------------------------------------------- 
def add_db (message, conn, cursor):
    '''Añadimos al usuario en la base de datos de username'''
    query = "SELECT * FROM username WHERE name like '@" + message.new_chat_members[0].username + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:            
        query = "SELECT MAX(id) AS ultimo_id FROM username"
        cursor.execute(query)
        results = cursor.fetchall()
        id = results[0][0]+1
        query = "INSERT INTO username (id, name) VALUES (" + str(id) + ", '@" + message.new_chat_members[0].username + "')"
        cursor.execute(query)
        conn.commit() #Importante para que se guarden los cambios de la consulta.

#Función para comprobar si en el mensaje hay palabrotas -------------------------------------------------------------------------------------------------------- 
def comprobar_palabrota(message, conn, cursor):
    '''Comprobamos que en el texto no haya palabrotas y baneamos en caso de encontra alguna'''
    haypalabrota = False
    mensaje = message.text.lower().split(" ")
    for palabra in mensaje:
        try:
            query = "SELECT * FROM badwords WHERE word like '" + palabra + "'"
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) != 0:
                haypalabrota = True
            #for row in results:
                #print(row)                    
        except:
            print (palabra + " no esta baneada")
    if haypalabrota:
        bot.delete_message(message.chat.id, message.message_id)
        query = "SELECT * FROM bannedusers WHERE user like '@" + message.from_user.username + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            query = "SELECT MAX(id) AS ultimo_id FROM bannedusers"
            cursor.execute(query)
            results = cursor.fetchall()
            id = results[0][0]+1
            query = "INSERT INTO bannedusers (id, name, warnings) VALUES (" + str(id) + ", '@" + message.from_user.username + "', 1)"
            cursor.execute(query)
            conn.commit() #Importante para que se guarden los cambios de la consulta.
            bot.send_message(message.chat.id, "Modera tu lenguaje, es tu primer aviso, al tercero serás baneado del grupo", parse_mode='html')
        else:
            if results[0][2] == 3:
                #Baneado del grupo
            else:
                query = "UPDATE bannedusers SET warnings = " + str(results[0][2]+1) + " WHERE name = '" + results[0][1] + "'"
                bot.send_message(message.chat.id, "Modera tu lenguaje, es tu segundo aviso, al tercero serás baneado del grupo", parse_mode='html')