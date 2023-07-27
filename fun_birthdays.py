# coding=utf-8
from config import *                        #Importamos el token y los id de grupo
from fun_mod import *                       #Necesitaremos las funciones del listado con botones y conexión con base de datos
import telebot                              #Para manejar la API de Telegram
from telebot.types import ForceReply        #Para forzar respuestas a mensajes
from datetime import *                      #Para el manejo de horas
from time import sleep                      #Para dormir al hilo

#Funciones /config o /configurar --------------------------------------------------------------------------------------------------------
def config(message, bot):
    '''Dependiendo de la respuesta configuramos texto o foto'''
    if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
        if message.content_type == "text":
            if message.text.lower() == "texto":
                text = "Para configurar un mensaje bonito, puedes escribir el texto entre <b> y </b> se monstrará en negrita. Si lo escribes entre <u> y </u> se escribirá subrayado." + "\n\n"
                text += "El texto:\n <b>Esto en negrita</b>\n<u>Esto subrayado</u>\nSe verá:"
                bot.send_message(message.chat.id, text)
                text = "<b>Esto en negrita</b>\n<u>Esto subrayado</u>"
                bot.send_message(message.chat.id, text, parse_mode = "html")
                bot.send_message(message.chat.id, "Por otro lado, si escribes '@', se sustituirá por el nombre o nombre de usuario de la persona que cumple años. Si escribes 'date', se sustituirá por la fecha. SSi escribes '\\n', tendrás un salto de línea en tu mensaje.")
                msg = bot.send_message(message.chat.id, "Ahora escribe el texto que quieres que guarde.\n\nIntenta que no supere los 250 caracteres.\n\nPodrás cambiarlo ejecutando otra vez el comando /config o /configurar.\n\nSi quieres cancelar el proceso, escribe 'salir' o 'exit'.")
                bot.register_next_step_handler(msg, save_text, bot)
            elif message.text.lower() == "foto":
                msg = bot.send_message(message.chat.id, "Envíame una foto y la guardaré para que se adjunte al mensaje de felicidades el día que haya algún cumpleaños.")
                bot.register_next_step_handler(msg, save_photo, bot)
            elif message.text.lower() == "salir" or message.text.lower() == "exit":
                bot.send_message(message.chat.id, "Proceso de configuración cancelado.")
            else:
                bot.send_message(message.chat.id, "Esa no es una opción. Si quieres, vuelve a intentarlo escribiendo otra vez el comando /config o /configurar.")
        else:
            bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")
    else:
        msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
        bot.register_next_step_handler(msg, config, bot)

def save_text(message, bot):
    '''Guardamos el texto en la base de datos'''
    if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
        if message.content_type == "text":
            if message.text.lower() != "salir" and message.text.lower() != "exit":
                if len(message.text) < 250:
                    conn = connect_db()
                    cursor = conn.cursor()
                    query = "SELECT * FROM messageconfig WHERE id = " + str(message.chat.id)
                    cursor.execute(query)
                    results = cursor.fetchall()
                    if len(results) == 0:
                        query = "INSERT INTO messageconfig (id, text, photo) VALUES (" + str(message.chat.id) + ", '" + message.text + "', NULL)"
                    else:
                        query = "UPDATE messageconfig SET text = '" + message.text + "'"
                    cursor.execute(query)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    bot.send_message(message.chat.id, "Texto de felicitación guardado.")
                else:
                    msg = bot.send_message(message.chat.id, "El mensaje no puede superar los 250 caracteres.\n\nPuedes volver a intentarlo o escribir 'salir' o 'exit' para cancelar.")
                    bot.register_next_step_handler(msg, save_text, bot)
            else:
                bot.send_message(message.chat.id, "Proceso de configuración cancelado.")
        else:
            bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")
    else:
        msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
        bot.register_next_step_handler(msg, save_text, bot)

def save_photo(message, bot):
    '''Guardamos la foto en la base de datos'''
    if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
        if message.content_type == "photo":
            id = message.json["photo"][0]["file_id"]
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT * FROM messageconfig WHERE id = " + str(message.chat.id)
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                query = "INSERT INTO messageconfig (id, text, photo) VALUES (" + str(message.chat.id) + ", NULL, '" + id + "')"
            else:
                query = "UPDATE messageconfig SET photo = '" + id + "' WHERE id = " + str(message.chat.id)
            cursor.execute(query)
            conn.commit()
            cursor.close()
            conn.close()
            bot.send_message(message.chat.id, "Foto de felicitación guardada.")
        else:
            if message.content_type == "text" and (message.text.lower() == "salir" or message.text.lower() == "exit"):
                bot.send_message(message.chat.id, "Proceso de configuración cancelado.")
            else:
                bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")
    else:
        msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
        bot.register_next_step_handler(msg, save_photo, bot)

#Funciones /add o /nuevo --------------------------------------------------------------------------------------------------------
def ask_date(message, bot, input):
    '''Preguntamos la fecha del cumpleaños'''
    if message.content_type == "text":
        if message.text.lower() != "salir" and message.text.lower() != "exit":
            user = message.text
            if message.chat.type == "private":
                query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
                cursor.execute(query)
                results = cursor.fetchall()
                if len(results) == 0:
                    input.append(user)
                    msg = bot.send_message(message.chat.id, "¿Cuándo es su cumpleaños?\n\nIndícalo en formato DD/MM.")
                    bot.register_next_step_handler(msg, new_birthday, bot, input)
                else:
                    bot.send_message(message.chat.id, "El cumpleaños de este usuario ya lo tengo registrado.\n\nPara cambiarlo, usa el comando /actualizar o /update.")
            else:
                if (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
                    query = "SELECT * FROM usernames WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
                    cursor.execute(query)
                    results = cursor.fetchall()
                    if len(results) == 0:
                        bot.send_message(message.chat.id, "Ese usuario no está registrado.\n\nPuedes registrarlo con el comando /register o /registrar.")
                    else:
                        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
                        cursor.execute(query)
                        results = cursor.fetchall()
                        if len(results) == 0:
                            input.append(user)
                            msg = bot.send_message(message.chat.id, "¿Cuándo es su cumpleaños?\n\nIndícalo en formato DD/MM.")
                            bot.register_next_step_handler(msg, new_birthday, bot, input)
                        else:
                            bot.send_message(message.chat.id, "El cumpleaños de este usuario ya lo tengo registrado.\n\nPara cambiarlo, usa el comando /actualizar o /update.")
                else:
                    msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
                    bot.register_next_step_handler(msg, ask_date, bot, input)
        else:
            bot.send_message(message.chat.id, "Proceso de añadir cumpleaños cancelado.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

def new_birthday(message, bot, input):
    '''Comprobamos que la fecha está correctamente'''
    if message.content_type == "text":
        if message.text.lower() != "exit" and message.text.lower() != "salir":
            date = message.text
            divDate = date.split("/")
            if len(divDate) == 2:
                mes_31 = ["01", "1", "03", "3", "05", "5", "07", "7", "08", "8", "10", "12"]
                if 1 <= int(divDate[1]) <= 12:
                    if (divDate[1] == "02") or (divDate[1] == "2"):
                        if 1 <= int(divDate[0]) <= 29:
                            if len(divDate[0]) == 1 and len(divDate[1]) == 1:
                                date = "0" + divDate[0] + "/0" + divDate[1]
                            elif len(divDate[0]) == 1 and len(divDate[1]) == 2:
                                date = "0" + date
                            elif len(divDate[0]) == 2 and len(divDate[1]) == 1:
                                date = divDate[0] + "/0" + divDate[1]
                            input.append(date)
                            save_birthday(message, bot, input)
                        else:
                            msg = bot.send_message(message.chat.id, "Febrero solo tiene 29 días.\n\nPor favor, introduce un día correcto o escribe 'salir' o 'exit' para cancelar.")
                            bot.register_next_step_handler(msg, new_birthday, bot, input)
                    elif divDate[1] in mes_31:
                        if 1 <= int(divDate[0]) <= 31:
                            if len(divDate[0]) == 1 and len(divDate[1]) == 1:
                                date = "0" + divDate[0] + "/0" + divDate[1]
                            elif len(divDate[0]) == 1 and len(divDate[1]) == 2:
                                date = "0" + date
                            elif len(divDate[0]) == 2 and len(divDate[1]) == 1:
                                date = divDate[0] + "/0" + divDate[1]
                            input.append(date)
                            save_birthday(message, bot, input)
                        else:
                            msg = bot.send_message(message.chat.id, "El mes introducido solo tiene 31 días.\n\nPor favor, introduce un día correcto o escribe 'salir' o 'exit' para cancelar.")
                            bot.register_next_step_handler(msg, new_birthday, bot, input)
                    else:
                        if 1 <= int(divDate[0]) <= 30:
                            if len(divDate[0]) == 1 and len(divDate[1]) == 1:
                                date = "0" + divDate[0] + "/0" + divDate[1]
                            elif len(divDate[0]) == 1 and len(divDate[1]) == 2:
                                date = "0" + date
                            elif len(divDate[0]) == 2 and len(divDate[1]) == 1:
                                date = divDate[0] + "/0" + divDate[1]
                            input.append(date)
                            save_birthday(message, bot, input)
                        else:
                            msg = bot.send_message(message.chat.id, "El mes introducido solo tiene 30 días.\n\nPor favor, introduce un día correcto o escribe 'salir' o 'exit' para cancelar.")
                            bot.register_next_step_handler(msg, new_birthday, bot, input)
                else:
                    msg = bot.send_message(message.chat.id, "Este mes no es válido.\n\nPor favor, introduce un mes válido o escribe 'salir' o 'exit' para cancelar.")
                    bot.register_next_step_handler(msg, new_birthday, bot, input)
            else:
                msg = bot.send_message(message.chat.id, "Por favor, introduce la fecha en formato DD/MM o escribe 'salir' o 'exit' para cancelar.")
                bot.register_next_step_handler(msg, new_birthday, bot, input)
        else:
            bot.send_message(message.chat.id, "Proceso de añadir cumpleaños cancelado.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

def save_birthday(message, bot, input):
    '''Añadimos el cumpleaños a la base de datos'''
    conn = connect_db()
    cursor = conn.cursor()
    if input[1] == "existe":
        query = "UPDATE birthdaydata SET date = '" + input[2] + "' WHERE name = '" + input[0] + "'"
    else:
        query = "SELECT MAX(id) AS ultimo_id FROM birthdaydata"
        cursor.execute(query)
        results = cursor.fetchall()
        id = 1
        if results[0][0] != None:
            id = results[0][0]+1
        query = "INSERT INTO birthdaydata (id, name, date, chatId, chatType) VALUES (" + str(id) + ", '" + input[0] + "', '" + input[1] + "', " + str(message.chat.id) + ", '" + message.chat.type + "')"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, "Cumpleaños guardado.")

#Función /view o /ver --------------------------------------------------------------------------------------------------------
def show_birthday(message, bot):
    '''Buscamos el usuario y lo mostramos por pantalla'''
    if message.content_type == "text":
        conn = connect_db()
        cursor = conn.cursor()
        if message.text.lower() == "todos":
            query = "SELECT name, date FROM birthdaydata WHERE chatId = " + str(message.chat.id)
            cursor.execute(query)
            results =  cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "No hay cumpleaños guardados.\n\nPuedes añadirlos con el comando /add o /nuevo.")
            else:
                query = "SELECT * FROM pagesdata where id = " + str(message.chat.id)
                cursor.execute(query)
                results2 = cursor.fetchall()
                if len(results2) == 0:
                    query = "INSERT INTO pagesdata (id, page, list) VALUES (" + str(message.chat.id) + ", 0, \"" + str(results) + "\")"
                else:
                    query = "UPDATE pagesdata SET page = 0, list = \"" + str(results) + "\" WHERE id = " + str(message.chat.id)
                cursor.execute(query)
                conn.commit()
                query = "SELECT * FROM pagesdata where id = " + str(message.chat.id)
                cursor.execute(query)
                results2 = cursor.fetchall()
                show_pages(results2, message.chat.id, None, bot)
        else:
            user = message.text
            query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "No tengo registrado el cumpleaños de este usuario.\n\nPuedes añadirlo con el comando /add o /nuevo.\n\nTambién puedes usar el comando /view o /ver e introduciendo 'todos', verás una lista de los cumpleaños almacenados.")
            else:
                bot.send_message(message.chat.id, "El cumpleaños de " + results[0][1] + " es el " + results[0][2] + ".")
        cursor.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función /update o /actualizar --------------------------------------------------------------------------------------------------------
def update_birthday(message, bot):
    '''Actualizamos un cumpleaños existente'''
    if message.content_type == "text":
        if (message.chat.type == "private") or (bot.get_chat_member(message.chat.id, message.from_user.id).status in ["creator", "administrator"]) or (message.chat.id == MY_CHAT_ID):
            if message.text.lower() != "exit" and message.text.lower() != "salir":
                user = message.text
                conn = connect_db()
                cursor = conn.cursor()
                query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
                cursor.execute(query)
                results = cursor.fetchall()
                cursor.close()
                conn.close()
                if len(results) == 0:
                    bot.send_message(message.chat.id, "No tengo registrado el cumpleaños de este usuario.\n\nPuedes añadirlo con el comando /add o /nuevo.\n\nTambién puedes usar el comando /view o /ver e introduciendo 'todos', verás una lista de los cumpleaños almacenados.")
                else:
                    msg = bot.send_message(message.chat.id, "Por favor, introduce la fecha en formato DD/MM.")
                    input = [user, "existe"]
                    bot.register_next_step_handler(msg, new_birthday, bot, input)
            else:
                bot.send_message(message.chat.id, "Proceso de actualizar cumpleaños cancelado.")
        else:
            msg = bot.send_message(message.chat.id, "Acción solo disponible para los administradores del grupo.\n\nPor favor, no interrumpas el proceso.\n\nEl administrador puede continuar o escribir 'salir' o 'exit' para cancelar.")
            bot.register_next_step_handler(msg, update_birthday, bot)
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función /delete o /borrar --------------------------------------------------------------------------------------------------------
def delete_birthday(message, bot):
    '''Borramos de la lista el cumpleaños'''
    if message.content_type == "text":
        user = ''
        if message.text.startswith("/"):
            user = "@" + message.from_user.username
        else:
            user = message.text
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            bot.send_message(message.chat.id, "No tengo registrado el cumpleaños de este usuario.\n\nTambién puedes usar el comando /view o /ver e introduciendo 'todos', verás una lista de los cumpleaños almacenados.")
        else:
            query = "DELETE FROM birthdaydata WHERE name like '" + user + "'"
            cursor.execute(query)
            conn.commit()
            bot.send_message(message.chat.id, "Cumpleaños borrado.")
        cursor.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función /test o /probar --------------------------------------------------------------------------------------------------------
def simulate_birthday(message, bot):
    '''Simulamos como mostraria el mensaje de felicitación'''
    if message.content_type == "text":
        user = message.text
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(results) == 0:
            bot.send_message(message.chat.id, "No tengo registrado el cumpleaños de este usuario.\n\nPuedes añadirlo con el comando /add o /nuevo.\n\nTambién puedes usar el comando /view o /ver e introduciendo 'todos', verás una lista de los cumpleaños almacenados.")
        else:
            happy_birthday(results[0], bot)
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Función de felicitar para simular y comprobar --------------------------------------------------------------------------------------------------------
def happy_birthday(i, bot):
    '''Muestra el texto y la foto definidos para felicitar el cumpleaños'''
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT * FROM messageconfig WHERE id = " + str(i[3])
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    text = ""
    photo = ""
    if len(results) == 0:
        #Textos y fotos por defecto
        if i[4] == "private":
            text += "<b><u>¡¡RECORDATORIO!!</u></b>\n"
            text += "Hoy, día " + i[2] + ", es el cumpleaños de " + i[1] + ", que no se te olvide desearle un feliz día!"
            bot.send_message(i[3], text, parse_mode = "html")
        else:
            photo = open("FelizCumple.jpg", "rb")
            text += "<b><u>¡¡FELIZ CUMPLEAÑOS!!</u></b>\n"
            text += "Hoy, día " + i[2] + ", es el cumpleaños de " + i[1] + " y todos queremos desearte un feliz día. 😘🥳"
            bot.send_photo(i[3], photo, text, parse_mode = "html")
    else:
        if results[0][1] != None:
            txt1 = results[0][1].replace("@", i[1])
            text += txt1.replace("date", i[2])
        else:
            if i[4] == "private":
                text += "<b><u>¡¡RECORDATORIO!!</u></b>\n"
                text += "Hoy, día " + i[2] + ", es el cumpleaños de " + i[1] + ", que no se te olvide desearle un feliz día!"
            else:
                text += "<b><u>¡¡FELIZ CUMPLEAÑOS!!</u></b>\n"
                text += "Hoy, día " + i[2] + ", es el cumpleaños de " + i[1] + " y todos queremos desearte un feliz día. 😘🥳"
        if results[0][2] != None:
            photo = results[0][2]
        else:
            if i[4] != "private":
                photo = open("FelizCumple.jpg", "rb")
        if i[4] == "private" and results[0][2] == None:
            bot.send_message(i[3], text, parse_mode = "html")
        else:
            bot.send_photo(i[3], photo, text, parse_mode = "html")

#Función principal diaria para comprobar los cumples --------------------------------------------------------------------------------------------------------
def verify_birthday(startDate, bot):
    '''Comprobamos si hay cumpleaños y esperamos un dia para comprobar el siguiente'''
    withBirthGroup = []
    today = datetime.now().strftime("%d/%m")
    if today > startDate:
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT * FROM birthdaydata WHERE date like '" + today + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            query = "SELECT DISTINCT chatId FROM birthdaydata WHERE chatType not like 'private'"
            cursor.execute(query)
            results = cursor.fetchall()
            for i in results:
                bot.send_message(i[0], "Hoy no hay cumpleaños.\n\nFeliz día a todos. 😘")
        else:
            for i in results:
                withBirthGroup.append(i[3])
                happy_birthday(i, bot)
            query = "SELECT DISTINCT chatId FROM birthdaydata WHERE chatType not like 'private'"
            cursor.execute(query)
            results = cursor.fetchall()
            for i in results:
                if i[0] not in withBirthGroup:
                    bot.send_message(i[0], "Hoy no hay cumpleaños.\n\nFeliz día a todos. 😘")
        cursor.close()
        conn.close()
    else:
        sleep(86400)
    verify_birthday(today, bot)