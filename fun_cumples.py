from config import *    #importamos el token y los id de grupo
import telebot  #para manejar la API de Telegram
from telebot.types import ForceReply    #citar un mensaje
from datetime import datetime   #para el manejo de horas
from pytz import timezone     #para las franjas horarias

#Funciones /add o /nuevo --------------------------------------------------------------------------------------------------------
def preguntar_zona_horaria(message, bot, entrada, conn, cursor):
    '''Preguntamos la zona horaria'''        
    user = message.text
    query = "SELECT * FROM usernames WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Ese usuario no está registrado, habla con un administrador para darte de alta o escribe un usuario correctamente con el @', reply_markup=markup)
        bot.register_next_step_handler(msg, preguntar_zona_horaria, bot, entrada, conn, cursor)
    else:
        query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
        cursor.execute(query)
        results = cursor.fetchall()
        if len(results) == 0:
            entrada.append(user)
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, '¿En qué país reside?', reply_markup=markup)
            bot.register_next_step_handler(msg, preguntar_fecha, bot, entrada, conn, cursor)
        else:
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Para este usuario ya hay un cumpleaños guardado, para cambiarlo usa el comando /actualizar o /update, introduce un usuario correctamente con el @', reply_markup=markup)
            bot.register_next_step_handler(msg, preguntar_zona_horaria, bot, entrada, conn, cursor)

def preguntar_fecha(message, bot, entrada, conn, cursor):
    '''Preguntamos la fecha del cumpleaños'''
    #ESTA LA DEJO PARA EL FINAL PORQUE NO SE MUY BIEN COMO HACERLA, de momento voy a cambiarla a modo de prueba
    '''pais = message.text.lower()
    if pais == "españa":
        pais = "espana"
    if (pais == "usa") or (pais == "eeuu"):
        pais = "estados unidos"
    if pais == "perú":
        pais = "peru"
    if (pais == "méxico") or (pais == "méjico") or (pais == "mejico"):
        pais = "mexico" 
    if pais == "panamá":
        pais = "panama"
    paises = open("DatosPaises.txt", "r")
    if -1 != paises.read().find(pais):
        entrada.append(pais)
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, "¿Cuándo es su cumpleaños?\nIndicalo en formato DD/MM.", reply_markup=markup)
        paises.close()
        bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)
    else:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Ese país no está en mi lista, por favor introduce un país válido.', reply_markup=markup)
        paises.close()
        bot.register_next_step_handler(msg, preguntar_fecha, bot, entrada, conn, cursor)'''
    entrada.append(message.text.lower())
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, "¿Cuándo es su cumpleaños?\nIndicalo en formato DD/MM.", reply_markup=markup)
    bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)
    
def nuevo_cumple(message, bot, entrada, conn, cursor):
    '''Comprobamos que la fecha está correctamente'''
    fecha = message.text
    fecha_div = fecha.split('/')
    if len(fecha_div) == 2:
        mes_31 = ['01', '1', '03', '3', '05', '5', '07', '7', '08', '8', '10', '12']
        if 1 <= int(fecha_div[1]) <= 12:
            if (fecha_div[1] == '02') or (fecha_div[1] == '2'):
                if 1 <= int(fecha_div[0]) <= 29:
                    entrada.append(fecha)
                    guardar_cumple(message, bot, entrada, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, 'Febrero solo tiene hasta 29 días, por favor introduce un día correcto.', reply_markup=markup)
                    bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)
            elif fecha_div[1] in mes_31:
                if 1 <= int(fecha_div[0]) <= 31:
                    entrada.append(fecha)
                    guardar_cumple(message, bot, entrada, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, 'El mes introducido tiene hasta 31 días, por favor introduce un día correcto.', reply_markup=markup)
                    bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)
            else:
                if 1 <= int(fecha_div[0]) <= 30:
                    entrada.append(fecha)
                    guardar_cumple(message, bot, entrada, conn, cursor)
                else:
                    markup = ForceReply()
                    msg = bot.send_message(message.chat.id, 'El mes introducido tiene hasta 30 días, por favor introduce un día correcto.', reply_markup=markup)
                    bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)        
        else:
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Ese mes no es válido, por favor introduce un mes válido.', reply_markup=markup)
            bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)
    else:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Por favor, introduce la fecha en formato DD/MM.', reply_markup=markup)
        bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)
    
def guardar_cumple(message, bot, entrada, conn, cursor):    
    '''Añadimos el cumpleaños a la base de datos'''
    if entrada[1] == "existe":
        query = "UPDATE birthdaydata SET date = '" + entrada[2] + "' WHERE name = '" + entrada[0] + "'"        
    else:
        query = "SELECT MAX(id) AS ultimo_id FROM birthdaydata"
        cursor.execute(query)
        results = cursor.fetchall()
        id = results[0][0]+1
        query = "INSERT INTO birthdaydata (id, name, timezone, date) VALUES (" + str(id) + ", '" + entrada[0] + "', '" + entrada[1] + "', '" + entrada[2] + "')"
    cursor.execute(query)
    conn.commit() #Importante para que se guarden los cambios de la consulta.
    bot.send_message(message.chat.id, 'Cumpleaños guardado.')
    entrada.clear()
  
#Funciones /update o /actualizar --------------------------------------------------------------------------------------------------------  
def actualizar_cumple(message, bot, conn, cursor):
    '''Actualizamos un cumpleaños existente'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Ese usuario no tiene un cumpleaños registrado, añadelo usando los comandos /add o /nuevo o escribe un usuario correctamente con el @', reply_markup=markup)
        bot.register_next_step_handler(msg, actualizar_cumple, bot, conn, cursor)
    else:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Por favor, introduce la fecha en formato DD/MM.', reply_markup=markup)
        entrada = [user, "existe"]
        bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)
    
    
#Funciones /view o /ver --------------------------------------------------------------------------------------------------------    
def mostrar_cumple(message, bot, conn, cursor):
    '''Buscamos el usuario y lo mostramos por pantalla'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        msg = bot.send_message(message.chat.id, "El cumpleaños de " + results[0][1] + " es el " + results[0][3])

#Funciones /delete o /borrar --------------------------------------------------------------------------------------------------------         
def borrar_cumple(message, bot, conn, cursor):
    '''Borramos de la lista el cumpleaños'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        query = "DELETE FROM birthdaydata WHERE name like '" + user + "'"
        cursor.execute(query)
        conn.commit() #Importante para que se guarden los cambios de la consulta.
        msg = bot.send_message(message.chat.id, "Cumpleaños borrado.")

#Funciones /test o /probar --------------------------------------------------------------------------------------------------------
def simular_cumple(message, bot, conn, cursor):
    '''Simulamos como mostraria el mensaje de felicitación'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        felicitar_cumple(results[0][3], user, bot)
    
#Funcion de felicitar para simular y comprobar --------------------------------------------------------------------------------------------------------    
def felicitar_cumple(dia, nombre, bot):
    '''Muestra el texto y la foto definidos para felicitar el cumpleaños'''
    photo = open("FelizCumple.jpg", "rb")
    text = '<b><u>¡¡FELIZ CUMPLEAÑOS!!</u></b>' + '\n'
    text += 'Hoy, día ' + dia + ', es el cumpleaños de ' + nombre + ' y todo el grupo queremos desearte un feliz día. 😘🥳'
    msg = bot.send_photo(MY_CHAT_ID, photo, text, parse_mode='html')

#Función principal diaria para comprobar los cumples --------------------------------------------------------------------------------------------------------
def comprobar_cumples(bot, conn, cursor):
    '''Comprobamos si hay cumpleaños el día de hoy'''
    hoy = datetime.now()
    hoyFormat = datetime.strftime(hoy, '%d/%m')
    query = "SELECT * FROM birthdaydata WHERE date like '" + hoyFormat + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(MY_CHAT_ID, "Hoy no hay cumpleaños, feliz día a todos. 😘")
    else:
        for i in results:
            felicitar_cumple(results[0][3], results[0][1], bot) 