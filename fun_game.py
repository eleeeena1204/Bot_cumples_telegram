import telebot                                  #Para manejar la API de Telegram
from telebot.types import ForceReply            #Para forzar respuestas a mensajes

def printHangman(lives):
    '''Dibujar la típica plantilla del juego'''
    text = '_____' + '\n'
    text += '|        |' + '\n'
    match lives: 
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
        
def initialText(bot, message):
    '''Mostrar el texto y la foto inicial del juego'''
    photo = open("ahorcado.png", "rb")
    text = '<b><u>Bienvendi@ al juego del Ahorcado o Hangman.</u></b>' + '\n'
    text += 'Introduce letras para adivinar la palabra oculta antes de que se te acaben los intentos.'
    bot.send_photo(message.from_user.id, photo, text, parse_mode='html')

#MAIN
def play(text, lives, selectedWord, inputLetters, bot, message, conn, cursor):
    '''Función para el funcionamiento del juego'''
    if lives == 0:
        text = '✰ Lo siento, has perdido 😥' + '\n' + '\n'
        text += printHangman(lives) + '\n'
        text += '✰ La palabra era: ' + selectedWord 
        bot.send_message(message.from_user.id, text)
    else:  
        fault = 0
        text += printHangman(lives) + '\n'
        text += '✰ Palabra a adivinar: '
        for letra in selectedWord:
            if letra in inputLetters:
                text += letra
            else:
                text += '_ '
                fault += 1
        if fault == 0:
            text = '✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨' + '\n'
            text += '✨   🥳 FELICIDADES, HAS GANADO 🥳   ✨' + '\n'
            text += '✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨'
            bot.send_message(message.from_user.id, text)
            query = "SELECT * FROM ranking WHERE id = " + str(message.from_user.id)
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
            text += '\n' + '✰ Letras ya introducidas: ' + inputLetters + '\n'
            bot.send_message(message.from_user.id, text)
            markup = ForceReply()
            newLetter = bot.send_message(message.from_user.id, "✰ Introduce una letra: ", reply_markup=markup)
            bot.register_next_step_handler(newLetter, add_new_letter, lives, selectedWord, inputLetters, bot, message, conn, cursor) 

def add_new_letter(newLetter, lives, selectedWord, inputLetters, bot, message, conn, cursor):
    '''Función para añadir iteración y seguir jugando'''
    text = ''
    if newLetter.text.lower() not in inputLetters:
        inputLetters += newLetter.text.lower() + ", "
        if newLetter.text.lower() not in selectedWord:
            lives -= 1
            text += '✰ La letra no está en la palabra. Te quedan ' + str(lives) + ' intentos.' + '\n'
        else:
            text += '✰ Letra correcta!' + '\n'
    else:
        text += '✰ Letra ya mencionada!' + '\n'    
    play(text, lives, selectedWord, inputLetters, bot, message, conn, cursor)