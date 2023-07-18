# coding=utf-8
from config import *                        #Importamos el token y los id de grupo
from bot_telegram import *                  #Necesitaremos las funciones del listado con botones
import telebot                              #Para manejar la API de Telegram
from telebot.types import ForceReply        #Para forzar respuestas a mensajes
from datetime import *                      #Para el manejo de horas
from time import sleep                      #Para dormir al hilo

#Funciones /config o /configurar --------------------------------------------------------------------------------------------------------
def config(message, bot, conn, cursor):
    '''Dependiendo de la respuesta llama a configurar texto o foto'''
    if message.text.lower() == "texto":
        config_text(message, bot, conn, cursor)
    elif message.text.lower() == "foto":
        config_photo(message, bot, conn, cursor)
    else:
        bot.send_message(message.chat.id, "Esa no es una opción, si quieres vuelve a intentarlo escribiendo otra vez el comando /config o /configurar.")

def config_text(message, bot, conn, cursor):
    '''Explicamos como configurar el texto y esperamos la respuesta'''
    text = "Para configurar un mensaje bonito puedes escribir el texto entre <b> y </b> se monstrará en negrita y si lo escribes entre <u> y </u> se escribirá subrayado." + "\n\n"
    text += "El texto:\n <b>Esto en negrita</b>\n<u>Esto subrayado</u>\nSe verá:"
    bot.send_message(message.chat.id, text)
    text = "<b>Esto en negrita</b>\n<u>Esto subrayado</u>"
    bot.send_message(message.chat.id, text, parse_mode = "html")
    bot.send_message(message.chat.id, "Por otro lado, si escribes '@' se sustituirá por el nombre o nombre de usuario de la persona que cumple años, si escribes 'date' se sustituirá por la fecha y si escribes '\\n' tendrás un salto de línea en tu mensaje.")
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "Ahora escribe el texto que quieres que guarde, podrás cambiarlo ejecutando otra vez el comando /config o /configurar", reply_markup = markup)
    bot.register_next_step_handler(msg, save_text, bot, conn, cursor)

def save_text(message, bot, conn, cursor):
    '''Guardamos el texto en la base de datos'''
    if message.content_type == "text":
        query = "SELECT * FROM messageconfig WHERE id = " + str(message.chat.id)
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            query = "INSERT INTO messageconfig (id, text, photo) VALUES (" + str(message.chat.id) + ", '" + message.text + "', NULL)"
        else:
            query = "UPDATE messageconfig SET text = '" + message.text + "'"
        cursor.execute(query)
        conn.commit()
        bot.send_message(message.chat.id, "Texto de felicitación guardado.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

def config_photo(message, bot, conn, cursor):
    '''Pedimos que envíe una foto para guardarla'''
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "Envíame una foto y la guardaré para que se adjunte al mensaje de felicidades el día que haya algún cumpleaños.", reply_markup = markup)
    bot.register_next_step_handler(msg, save_photo, bot, conn, cursor)

def save_photo(message, bot, conn, cursor):
    '''Guardamos la foto en la base de datos'''
    if message.content_type == "photo":
        id = message.json["photo"][0]["file_id"]
        query = "SELECT * FROM messageconfig WHERE id = " + str(message.chat.id)
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            query = "INSERT INTO messageconfig (id, text, photo) VALUES (" + str(message.chat.id) + ", NULL, '" + id + "')"
        else:
            query = "UPDATE messageconfig SET photo = '" + id + "' WHERE id = " + str(message.chat.id)
        cursor.execute(query)
        conn.commit()
        bot.send_message(message.chat.id, "Foto de felicitación guardado.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")
    
#Funciones /add o /nuevo --------------------------------------------------------------------------------------------------------
def ask_date(message, bot, input, conn, cursor):
    '''Preguntamos la fecha del cumpleaños'''
    if message.content_type == "text":
        user = message.text
        if message.chat.type == "private":
            query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                input.append(user)
                markup = ForceReply()
                msg = bot.send_message(message.chat.id, "¿Cuándo es su cumpleaños?\n\nIndicalo en formato DD/MM.", reply_markup = markup)
                bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
            else:
                bot.send_message(message.chat.id, "Para este usuario ya hay un cumpleaños guardado, para cambiarlo usa el comando /actualizar o /update.")
        else:
            query = "SELECT * FROM usernames WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "Ese usuario no está registrado, habla con un administrador para darle de alta o habisale de que se registre con el comando /register o /registrar.")
            else:
                query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
                cursor.execute(query)
                results = cursor.fetchall()
                if len(results) == 0:
                    input.append(user)
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, "¿Cuándo es su cumpleaños?\n\nIndicalo en formato DD/MM.", reply_markup = markup)
                    bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
                else:
                    bot.send_message(message.chat.id, "Para este usuario ya hay un cumpleaños guardado, para cambiarlo usa el comando /actualizar o /update.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

def new_birthday(message, bot, input, conn, cursor):
    '''Comprobamos que la fecha está correctamente'''
    if message.content_type == "text":
        if message.text != "exit" and message.text != "salir":
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
                            save_birthday(message, bot, input, conn, cursor)
                        else:
                            markup = ForceReply()
                            msg = bot.send_message(message.chat.id, "Febrero solo tiene hasta 29 días, por favor introduce un día correcto o escribe 'salir' o 'exit' para cancelar.", reply_markup = markup)
                            bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
                    elif divDate[1] in mes_31:
                        if 1 <= int(divDate[0]) <= 31:
                            if len(divDate[0]) == 1 and len(divDate[1]) == 1:
                                date = "0" + divDate[0] + "/0" + divDate[1]
                            elif len(divDate[0]) == 1 and len(divDate[1]) == 2:
                                date = "0" + date
                            elif len(divDate[0]) == 2 and len(divDate[1]) == 1:
                                date = divDate[0] + "/0" + divDate[1]
                            input.append(date)
                            save_birthday(message, bot, input, conn, cursor)
                        else:
                            markup = ForceReply()
                            msg = bot.send_message(message.chat.id, "El mes introducido tiene hasta 31 días, por favor introduce un día correcto o escribe 'salir' o 'exit' para cancelar.", reply_markup = markup)
                            bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
                    else:
                        if 1 <= int(divDate[0]) <= 30:
                            if len(divDate[0]) == 1 and len(divDate[1]) == 1:
                                date = "0" + divDate[0] + "/0" + divDate[1]
                            elif len(divDate[0]) == 1 and len(divDate[1]) == 2:
                                date = "0" + date
                            elif len(divDate[0]) == 2 and len(divDate[1]) == 1:
                                date = divDate[0] + "/0" + divDate[1]
                            input.append(date)
                            save_birthday(message, bot, input, conn, cursor)
                        else:
                            markup = ForceReply()
                            msg = bot.send_message(message.chat.id, "El mes introducido tiene hasta 30 días, por favor introduce un día correcto o escribe 'salir' o 'exit' para cancelar.", reply_markup = markup)
                            bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, "Ese mes no es válido, por favor introduce un mes válido o escribe 'salir' o 'exit' para cancelar.", reply_markup = markup)
                    bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
            else:
                markup = ForceReply()
                msg = bot.send_message(message.chat.id, "Por favor, introduce la fecha en formato DD/MM o escribe 'salir' o 'exit' para cancelar.", reply_markup = markup)
                bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
        else:
            bot.send_message(message.chat.id, "Se ha cancelado el añadir el cumpleaños de usuario.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

def save_birthday(message, bot, input, conn, cursor):
    '''Añadimos el cumpleaños a la base de datos'''
    if message.content_type == "text":
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
        bot.send_message(message.chat.id, "Cumpleaños guardado.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Funciones /view o /ver --------------------------------------------------------------------------------------------------------
def show_birthday(message, bot, conn, cursor):
    '''Buscamos el usuario y lo mostramos por pantalla'''
    if message.content_type == "text":
        if message.text.lower() == "todos":
            query = "SELECT name, date FROM birthdaydata WHERE chatId = " + str(message.chat.id)
            cursor.execute(query)
            results =  cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "No hay cumpleaños guardados, puedes añadirlos con el comando /add o /nuevo.")
            else:
                show_pages(results, message.chat.id, 0, None)
        else:
            user = message.text
            query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
            else:
                bot.send_message(message.chat.id, "El cumpleaños de " + results[0][1] + " es el " + results[0][2] + ".")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Funciones /update o /actualizar --------------------------------------------------------------------------------------------------------
def update_birthday(message, bot, conn, cursor):
    '''Actualizamos un cumpleaños existente'''
    if message.content_type == "text":
        user = message.text
        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            bot.send_message(message.chat.id, "Ese usuario no tiene un cumpleaños registrado, añadelo usando los comandos /add o /nuevo.")
        else:
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, "Por favor, introduce la fecha en formato DD/MM.", reply_markup=markup)
            input = [user, "existe"]
            bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Funciones /delete o /borrar --------------------------------------------------------------------------------------------------------
def delete_birthday(message, bot, conn, cursor):
    '''Borramos de la lista el cumpleaños'''
    if message.content_type == "text":
        user = message.text
        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
        else:
            query = "DELETE FROM birthdaydata WHERE name like '" + user + "'"
            cursor.execute(query)
            conn.commit()
            bot.send_message(message.chat.id, "Cumpleaños borrado.")
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Funciones /test o /probar --------------------------------------------------------------------------------------------------------
def simulate_birthday(message, bot, conn, cursor):
    '''Simulamos como mostraria el mensaje de felicitación'''
    if message.content_type == "text":
        user = message.text
        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "' and chatId = " + str(message.chat.id)
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
        else:
            print(results)
            happy_birthday(results[0], bot, conn, cursor)
    else:
        bot.send_message(message.chat.id, "Vaya, esto no es lo que esperaba...")

#Funcion de felicitar para simular y comprobar --------------------------------------------------------------------------------------------------------
def happy_birthday(i, bot, conn, cursor):
    '''Muestra el texto y la foto definidos para felicitar el cumpleaños'''
    query = "SELECT * FROM messageconfig WHERE id = " + str(i[3])
    cursor.execute(query)
    results = cursor.fetchall()
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
            text += "Hoy, día " + i[2] + ", es el cumpleaños de " + i[1] + " y todo el grupo queremos desearte un feliz día. 😘🥳"
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
                text += "Hoy, día " + i[2] + ", es el cumpleaños de " + i[1] + " y todo el grupo queremos desearte un feliz día. 😘🥳"
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
def verify_birthday(startDate, bot, conn, cursor):
    '''Comprobamos si hay cumpleaños y esperamos un dia para comprobar el siguiente'''
    withBirthGroup = []
    today = datetime.now().strftime("%d/%m")
    if today > startDate:
        query = "SELECT * FROM birthdaydata WHERE date like '" + today + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            query = "SELECT DISTINCT chatId FROM birthdaydata WHERE chatType not like 'private'"
            cursor.execute(query)
            results = cursor.fetchall()
            for i in results:
                bot.send_message(i, "Hoy no hay cumpleaños, feliz día a todos. 😘")
        else:
            for i in results:
                withBirthGroup.append(i[3])
                happy_birthday(i, bot, conn, cursor)
            query = "SELECT DISTINCT chatId FROM birthdaydata WHERE chatType not like 'private'"
            cursor.execute(query)
            results = cursor.fetchall()
            for i in results:
                if i[0] not in withBirthGroup:
                    bot.send_message(i[0], "Hoy no hay cumpleaños, feliz día a todos. 😘")
    else:
        sleep(86400)
    verify_birthday(today, bot, conn, cursor)