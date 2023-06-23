from config import *    #importamos el token y los id de grupo
import telebot  #para manejar la API de Telegram
from telebot.types import ReplyKeyboardMarkup   #botones y demás
from telebot.types import ForceReply    #citar un mensaje
import os   #para borrar lineas en un fichero
from datetime import datetime   #para el manejo de horas
from pytz import timezone     #para las franjas horarias

#Funciones /add o /nuevo --------------------------------------------------------------------------------------------------------
def preguntar_zona_horaria(message, bot, entrada, conn, cursor):
    '''Preguntamos la zona horaria'''
    '''nombre = message.text
    file = open("DatosCumples.txt", "r")  
    users = open("DatosUsuarios.txt", "r")
    if -1 != users.read().find(nombre):
        if -1 == file.read().find(nombre):
            entrada.append(nombre)
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, '¿En qué país reside?', reply_markup=markup)
            file.close()
            users.close()
            bot.register_next_step_handler(msg, preguntar_fecha, bot, entrada)
        else:
            msg = bot.send_message(message.chat.id, 'Para este usuario ya hay un cumpleaños guardado, para cambiarlo primero bórralo y añádelo de nuevo.') 
            file.close()
            users.close()
    else:
        markup = ForceReply()
        msg = bot.send_message(message.chat.id, 'Ese usuario no está en mi lista de marineras, por favor introduce un nombre válido con su @.', reply_markup=markup)
        file.close()
        users.close()
        bot.register_next_step_handler(msg, preguntar_zona_horaria, bot, entrada)'''
        
    #Base de datos
    user = message.text
    query = "SELECT * FROM username WHERE name like '" + user + "'"
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
            entrada.append(nombre)
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, '¿En qué país reside?', reply_markup=markup)
            bot.register_next_step_handler(msg, preguntar_fecha, bot, entrada, conn, cursor)
        else:
            markup = ForceReply()
            msg = bot.send_message(message.chat.id, 'Para este usuario ya hay un cumpleaños guardado, para cambiarlo usa el comando /actualizar o /update', reply_markup=markup)
            bot.register_next_step_handler(msg, preguntar_zona_horaria, bot, entrada, conn, cursor)

def preguntar_fecha(message, bot, entrada, conn, cursor):
    '''Preguntamos la fecha del cumpleaños'''
    #ESTA LA DEJO PARA EL FINAL PORQUE NO SE MUY BIEN COMO HACERLA
    pais = message.text.lower()
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
        bot.register_next_step_handler(msg, preguntar_fecha, bot, entrada, conn, cursor)
    
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
    '''file = open("DatosCumples.txt", "a")
    file.write('\n')
    for i in entrada:
        file.write(i + ';')
    file.close()'''
    if entrada[1] == "existe":
        query = "UPDATE birthdaydata SET date = " + entrada[2] + " WHERE name = '" + entrada[0] + "'"        
    else:
        query = "SELECT MAX(id) AS ultimo_id FROM birthdaydata"
        cursor.execute(query)
        results = cursor.fetchall()
        id = results[0][0]+1
        query = "INSERT INTO birthdaydata (id, name, date, timezone) VALUES (" + str(id) + ", '" + entrada[0] + "', " + str(entrada[1]) + ", '" + str(entrada[2]) + "')"
    cursor.execute(query)
    conn.commit() #Importante para que se guarden los cambios de la consulta.
    bot.send_message(message.chat.id, 'Cumpleaños guardado.')
    entrada.clear()
    
#Funciones /view o /ver --------------------------------------------------------------------------------------------------------    
def mostrar_cumple(message, bot):
    '''Buscamos el usuario y lo mostramos por pantalla'''
    '''nombre = message.text
    file = open("DatosCumples.txt", "r")
    if -1 == file.read().find(nombre):
        file.close()
        msg = bot.send_message(message.chat.id, "Del usuario introducido no se cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        file.close()
        file = open("DatosCumples.txt", "r")
        lineas = file.read().split('\n')
        for i in lineas:
            datos = i.split(';')
            if datos[0] == nombre:
                msg = bot.send_message(message.chat.id, "El cumpleaños de " + nombre + " es el " + datos[2])
        file.close()'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        msg = bot.send_message(message.chat.id, "El cumpleaños de " + results[0][1] + " es el " + results[0][2])

#Funciones /update o /actualizar --------------------------------------------------------------------------------------------------------  
def actualizar_cumple(message, bot, conn, cursor):
    '''Actualizamos un cumpleaños existente'''
    markup = ForceReply()
    msg = bot.send_message(message.chat.id, 'Por favor, introduce la fecha en formato DD/MM.', reply_markup=markup)
    entrada = [nombre, "existe"]
    bot.register_next_step_handler(msg, nuevo_cumple, bot, entrada, conn, cursor)

#Funciones /delete o /borrar --------------------------------------------------------------------------------------------------------         
def borrar_cumple(message, bot):
    '''Borramos de la lista el cumpleaños'''
    '''nombre = message.text
    file = open("DatosCumples.txt", "r")
    if -1 == file.read().find(nombre):
        file.close()
        msg = bot.send_message(message.chat.id, "Del usuario introducido no sé cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        file.close()
        file = open("DatosCumples.txt", "r")
        file_aux = open("DatosCumplesAux.txt", "w")
        for line in file:
            if nombre not in line.strip('\n'):
                file_aux.write(line)        
        file.close()
        file_aux.close()
        os.replace('DatosCumplesAux.txt', 'DatosCumples.txt')
        msg = bot.send_message(message.chat.id, "Cumpleaños borrado.") '''
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
def simular_cumple(message, bot):
    '''nombre = message.text
    file = open("DatosCumples.txt", "r")
    if -1 == file.read().find(nombre):
        file.close()
        msg = bot.send_message(message.chat.id, "Del usuario introducido no sé cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        file.close()
        file = open("DatosCumples.txt", "r")
        lineas = file.read().split('\n')
        for i in lineas:
            datos = i.split(';')
            if datos[0] == nombre:
                felicitar_cumple(datos[2], nombre, bot)
                
        file.close()'''
    user = message.text
    query = "SELECT * FROM birthdaydata WHERE name like '" + user + "'"
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        msg = bot.send_message(message.chat.id, "Del usuario introducido no tengo registrado cuando es su cumpleaños, añádelo usando el comando /add o /nuevo.")
    else:
        felicitar_cumple(results[0][2], user, bot)
    
#Funcion de felicitar para simular y comprobar --------------------------------------------------------------------------------------------------------    
def felicitar_cumple(dia, nombre, bot):
    '''photo = open("FotoCumple.jpeg", "rb")
    text = '<b><u>¡¡FELIZ CUMPLEAÑOS MARINERA!!</u></b>' + '\n'
    text += 'Hoy, día ' + dia + ', es el cumpleaños de ' + nombre + ' y todo el grupo de marineras queremos desearte un feliz día. 😘'
    msg = bot.send_photo(MY_CHAT_ID, photo, text, parse_mode='html')'''
    photo = open("FelizCumple.jpeg", "rb")
    text = '<b><u>¡¡FELIZ CUMPLEAÑOS!!</u></b>' + '\n'
    text += 'Hoy, día ' + dia + ', es el cumpleaños de ' + nombre + ' y todo el grupo queremos desearte un feliz día. 😘🥳'
    msg = bot.send_photo(message.chat.id, photo, text, parse_mode='html')

#Función principal diaria para comprobar los cumples --------------------------------------------------------------------------------------------------------
def comprobar_cumples(bot, conn, cursor):
    '''hoy = datetime.now()
    hoyFormat = datetime.strftime(hoy, '%d/%m')
    file = open("DatosCumples.txt", "r")
    if -1 == file.read().find(hoyFormat):
        file.close()
        msg = bot.send_message(MY_CHAT_ID, "Hoy no hay cumpleaños, feliz día a todas. 😘")
    else:
        file.close()
        file = open("DatosCumples.txt", "r")
        lineas = file.read().split('\n')
        for i in lineas:
            datos = i.split(';')
            if datos[2] == hoyFormat:
                felicitar_cumple(datos[2], datos[0], bot)
        file.close()'''
    hoy = datetime.now()
    hoyFormat = datetime.strftime(hoy, '%d/%m')
    query = "SELECT * FROM birthdaydata WHERE date like " + hoyFormat
    cursor.execute(query)
    results = cursor.fetchall()
    if len(results) == 0:
        bot.send_message(MY_CHAT_ID, "Hoy no hay cumpleaños, feliz día a todas. 😘")
    else:
        for i in results:
            felicitar_cumple(results[0][2], user, bot) 