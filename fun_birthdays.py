from config import *                        #Importamos el token y los id de grupo
import telebot                              #Para manejar la API de Telegram
from telebot.types import ForceReply        #Para forzar respuestas a mensajes
from datetime import *                      #Para el manejo de horas
from time import sleep                      #Para dormir al hilo

#Funciones /add o /nuevo --------------------------------------------------------------------------------------------------------
def ask_date(message, bot, input, conn, cursor):
    '''Preguntamos la fecha del cumpleaños'''        
    user = message.text
    query = "SELECT * FROM usernames WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Ese usuario no está registrado, habla con un administrador para darte de alta o vuelve a introducir el comando /add o /nuevo con un usuario correctamente con el @', reply_markup=markup)
    else:
        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            input.append(user)
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, "¿Cuándo es su cumpleaños?\nIndicalo en formato DD/MM.", reply_markup=markup)
            bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
        else:
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Para este usuario ya hay un cumpleaños guardado, para cambiarlo usa el comando /actualizar o /update', reply_markup=markup)
    
def new_birthday(message, bot, input, conn, cursor):
    '''Comprobamos que la fecha está correctamente'''
    date = message.text
    divDate = date.split('/')
    if len(divDate) == 2:
        mes_31 = ['01', '1', '03', '3', '05', '5', '07', '7', '08', '8', '10', '12']
        if 1 <= int(divDate[1]) <= 12:
            if (divDate[1] == '02') or (divDate[1] == '2'):
                if 1 <= int(divDate[0]) <= 29:
                    input.append(date)
                    save_birthday(message, bot, input, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, 'Febrero solo tiene hasta 29 días, por favor introduce un día correcto.', reply_markup=markup)
                    bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
            elif divDate[1] in mes_31:
                if 1 <= int(divDate[0]) <= 31:
                    input.append(date)
                    save_birthday(message, bot, input, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, 'El mes introducido tiene hasta 31 días, por favor introduce un día correcto.', reply_markup=markup)
                    bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
            else:
                if 1 <= int(divDate[0]) <= 30:
                    input.append(date)
                    save_birthday(message, bot, input, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, 'El mes introducido tiene hasta 30 días, por favor introduce un día correcto.', reply_markup=markup)
                    bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)        
        else:
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Ese mes no es válido, por favor introduce un mes válido.', reply_markup=markup)
            bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
    else:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Por favor, introduce la fecha en formato DD/MM.', reply_markup=markup)
        bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)
    
def save_birthday(message, bot, input, conn, cursor):    
    '''Añadimos el cumpleaños a la base de datos'''
    if input[1] == "existe":
        query = "UPDATE birthdaydata SET date = '" + input[2] + "' WHERE name = '" + input[0] + "'"        
    else:
        query = "SELECT MAX(id) AS ultimo_id FROM birthdaydata"
        cursor.execute(query)
        results = cursor.fetchall()
        id = 1
        if len(results) != 0:
            id = results[0][0]+1
        query = "INSERT INTO birthdaydata (id, name, date) VALUES (" + str(id) + ", '" + input[0] + "', '" + input[1] + "')"
    cursor.execute(query)
    conn.commit()
    bot.send_message(message.chat.id, "Cumpleaños guardado.")
  
#Funciones /view o /ver --------------------------------------------------------------------------------------------------------    
def show_birthday(message, bot, conn, cursor):
    '''Buscamos el usuario y lo mostramos por pantalla'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
       bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo")
    else:
        bot.send_message(message.chat.id, "El cumpleaños de " + results[0][1] + " es el " + results[0][2])

#Funciones /update o /actualizar --------------------------------------------------------------------------------------------------------  
def update_birthday(message, bot, conn, cursor):
    '''Actualizamos un cumpleaños existente'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Ese usuario no tiene un cumpleaños registrado, añadelo usando los comandos /add o /nuevo")
    else:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Por favor, introduce la fecha en formato DD/MM.', reply_markup=markup)
        input = [user, "existe"]
        bot.register_next_step_handler(msg, new_birthday, bot, input, conn, cursor)

#Funciones /delete o /borrar --------------------------------------------------------------------------------------------------------         
def delete_birthday(message, bot, conn, cursor):
    '''Borramos de la lista el cumpleaños'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo, si te has equivocado, vuelve a escribir /delete o /borrar para probar con el usuario correcto con su @")
    else:
        query = "DELETE FROM birthdaydata WHERE name like '" + user + "'"
        cursor.execute(query)
        conn.commit()
        msg = bot.send_message(message.chat.id, "Cumpleaños borrado.")

#Funciones /test o /probar --------------------------------------------------------------------------------------------------------
def simulate_birthday(message, bot, conn, cursor):
    '''Simulamos como mostraria el mensaje de felicitación'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        happy_birthday(results[0][3], user, bot)
    
#Funcion de felicitar para simular y comprobar --------------------------------------------------------------------------------------------------------    
def happy_birthday(dia, nombre, bot):
    '''Muestra el texto y la foto definidos para felicitar el cumpleaños'''
    photo = open("FelizCumple.jpg", "rb")
    text = '<b><u>¡¡FELIZ CUMPLEAÑOS!!</u></b>' + '\n'
    text += 'Hoy, día ' + dia + ', es el cumpleaños de ' + nombre + ' y todo el grupo queremos desearte un feliz día. 😘🥳'
    msg = bot.send_photo(GRUPO_ID, photo, text, parse_mode='html')

#Función principal diaria para comprobar los cumples --------------------------------------------------------------------------------------------------------
def verify_birthday(startDate, bot, conn, cursor):
    '''Comprobamos si hay cumpleaños y esperamos un dia para comprobar el siguiente'''
    today = datetime.now().strftime('%d/%m')
    if today > startDate:
        query = "SELECT * FROM birthdaydata WHERE date like '" + today + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            bot.send_message(GRUPO_ID, "Hoy no hay cumpleaños, feliz día a todos. 😘")
        else:
            for i in results:
                happy_birthday(results[0][2], results[0][1], bot)         
    else:
        sleep(86400)
    verify_birthday(today, bot, conn, cursor)