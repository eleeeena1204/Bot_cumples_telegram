#Ahorcado
import telebot  #para manejar la API de Telegram
from telebot.types import ForceReply    #citar un mensaje

def imprimirAhorcado(vidas):
    '''Dibujar la típica plantilla del juego'''
    text = '_____' + '\n'
    text += '|        |' + '\n'
    match vidas: 
        case 6:        
            text += '|' + '\n'
            text += '|' + '\n'
            text += '|' + '\n'
        case 5:
            text += '|      😵' + '\n'
            text += '|' + '\n'
            text += '|' + '\n'
        case 4:
            text += '|      😵' + '\n'
            text += '|       |' + '\n'
            text += '|' + '\n'
        case 3:
            text += '|      😵' + '\n'
            text += '|      /|' + '\n'
            text += '|' + '\n'
        case 2:
            text += '|      😵' + '\n'
            text += '|      /|\ ' + '\n'
            text += '|' + '\n'
        case 1:
            text += '|      😵' + '\n'
            text += '|      /|\ ' + '\n'
            text += '|      /' + '\n'
        case 0:
            text += '|      😵' + '\n'
            text += '|      /|\ ' + '\n'
            text += '|      / \ ' + '\n'
    text += '| _____' + '\n'
    return text
        
def textoInicial(bot, message):
    '''Mostrar el texto y la foto inicial del juego'''
    photo = open("ahorcado.png", "rb")
    text = '<b><u>Bienvendi@ al juego del Ahorcado o Hangman.</u></b>' + '\n'
    text += 'Introduce letras para adivinar la palabra oculta antes de que se te acaben los intentos.'
    bot.send_photo(message.from_user.id, photo, text, parse_mode='html')

#MAIN
def jugar(text, vidas, palabraElegida, letrasDichas, bot, message, conn, cursor):
    '''Función para el funcionamiento del juego'''
    if vidas == 0:
        text = '✰ Lo siento, has perdido 😥' + '\n' + '\n'
        text += imprimirAhorcado(vidas) + '\n'
        text += '✰ La palabra era: ' + palabraElegida 
        msg = bot.send_message(message.from_user.id, text, parse_mode='html')
    else:  
        fallas = 0
        text += imprimirAhorcado(vidas) + '\n'
        text += '✰ Palabra a adivinar: '
        for letra in palabraElegida:
            if letra in letrasDichas:
                text += letra
            else:
                text += '_ '
                fallas += 1
        if fallas == 0:
            text = '✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨' + '\n'
            text += '✨   🥳 FELICIDADES, HAS GANADO 🥳   ✨' + '\n'
            text += '✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨'
            msg = bot.send_message(message.from_user.id, text, parse_mode='html')
            query = "SELECT * FROM ranking WHERE id = " + message.from_user.id
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                query = "INSERT INTO ranking (id, name, score) VALUES (" + str(message.from_user.id) + ", '@" + message.from_user.username + "', 1)"
                cursor.execute(query)
                conn.commit() #Importante para que se guarden los cambios de la consulta.
            else:
                query = "UPDATE ranking SET score = " + str(results[0][2]+1) + " WHERE name = '" + results[0][1] + "'"
                cursor.execute(query)
                conn.commit()
        else:
            text += '\n' + '✰ Letras ya introducidas: ' + letrasDichas + '\n'
            msg = bot.send_message(message.from_user.id, text, parse_mode='html')
            markup = ForceReply()
            letraIntroducida = bot.send_message(message.from_user.id, "✰ Introduce una letra: ", reply_markup=markup)
            bot.register_next_step_handler(letraIntroducida, nuevaLetra, vidas, palabraElegida, letrasDichas, bot, message, conn, cursor) 

def nuevaLetra(letraIntroducida, vidas, palabraElegida, letrasDichas, bot, message, conn, cursor):
    '''Función para añadir iteración y seguir jugando'''
    text = ''
    if letraIntroducida.text not in letrasDichas:
        letrasDichas += letraIntroducida.text + ", "
        if letraIntroducida.text not in palabraElegida:
            vidas -= 1
            text += '✰ La letra no está en la palabra. Te quedan ' + str(vidas) + ' intentos.' + '\n'
        else:
            text += '✰ Letra correcta!' + '\n'
    else:
        text += '✰ Letra ya mencionada!' + '\n'    
    jugar(text, vidas, palabraElegida, letrasDichas, bot, message.from_user.id, conn, cursor)