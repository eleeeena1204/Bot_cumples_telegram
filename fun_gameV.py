# coding=utf-8
import telebot                                  #Para manejar la API de Telegram
from fun_mod import *                           #Necesitaremos la conexión con base de datos

#Función que muestra el dibujo del ahorcado --------------------------------------------------------------------------------------------------------
def print_hangman(lives):
    '''Dibujar la típica plantilla del juego'''
    text = '_____' + '\n'
    text += '|        |' + '\n'
    if lives == 6:
            text += '|' + '\n'
            text += '|' + '\n'
            text += '|' + '\n'
    elif lives == 5:
            text += '|       😵' + '\n'
            text += '|' + '\n'
            text += '|' + '\n'
    elif lives == 4:
            text += '|       😵' + '\n'
            text += '|       |' + '\n'
            text += '|' + '\n'
    elif lives == 3:
            text += '|       😵' + '\n'
            text += '|      /|' + '\n'
            text += '|' + '\n'
    elif lives == 2:
            text += '|       😵' + '\n'
            text += '|      /|\ ' + '\n'
            text += '|' + '\n'
    elif lives == 1:
            text += '|       😵' + '\n'
            text += '|      /|\ ' + '\n'
            text += '|      /' + '\n'
    elif lives == 0:
            text += '|       😵' + '\n'
            text += '|      /|\ ' + '\n'
            text += '|      / \ ' + '\n'
    text += '| _____' + '\n'
    return text

#Función de texto de inicio del juego --------------------------------------------------------------------------------------------------------
def initial_text(bot, message):
    '''Mostrar el texto y la foto inicial del juego'''
    photo = open("ahorcado.png", "rb")
    text = '<b><u>Bienvendi@ al juego del Ahorcado o Hangman.</u></b>\n'
    text += 'Introduce letras para adivinar la palabra oculta antes de que se te acaben los intentos.'
    bot.send_photo(message.from_user.id, photo, text, parse_mode = 'html')

#Función /hangman o /ahorcado --------------------------------------------------------------------------------------------------------
def play_hangman(text, lives, selectedWord, clue, inputLetters, bot, message):
    '''Función para el funcionamiento del juego'''
    if lives == 0:
        text = '? Lo siento, has perdido ??' + '\n\n'
        text += print_hangman(lives) + '\n'
        text += '? La palabra era: ' + selectedWord
        bot.send_message(message.from_user.id, text)
    else:
        fault = 0
        text += print_hangman(lives) + '\n'
        text += '? Pista: ' + clue + '\n'
        text += '? Palabra oculta: '
        for letra in selectedWord:
            if letra in inputLetters:
                text += letra
            else:
                text += '_ '
                fault += 1
        if fault == 0:
            text = '??? FELICIDADES, HAS GANADO ???' + '\n'
            text += '? La palabra era: ' + selectedWord + '\n'
            bot.send_message(message.from_user.id, text)
            user = ""
            if message.from_user.username == None:
                user = message.from_user.first_name
            else:
                user = "@" + message.from_user.username
            conn = connect_db()
            cursor = conn.cursor()
            query = "SELECT * FROM ranking WHERE id = " + str(message.from_user.id)
            cursor.execute(query)
            results = cursor.fetchall()
            if len(results) == 0:
                query = "INSERT INTO ranking (id, name, score) VALUES (" + str(message.from_user.id) + ", '" + user + "', 1)"
                cursor.execute(query)
                conn.commit() 
            else:
                query = "UPDATE ranking SET score = " + str(results[0][2]+1) + " WHERE id = " + str(message.from_user.id)
                cursor.execute(query)
                conn.commit()
            cursor.close()
            conn.close()
        else:
            text += '\n' + '? Letras ya introducidas: ' + inputLetters + '\n'
            text += '? Introduce una letra: '
            newLetter = bot.send_message(message.from_user.id, text)
            bot.register_next_step_handler(newLetter, add_new_letter, lives, selectedWord, clue, inputLetters, bot, message)

#Función para continuar el juego añadiendo letras --------------------------------------------------------------------------------------------------------
def add_new_letter(newLetter, lives, selectedWord, clue, inputLetters, bot, message):
    '''Función para añadir iteración y seguir jugando'''
    text = ''
    if message.content_type == 'text':
        if len(newLetter.text) == 1:
            if newLetter.text.lower() not in inputLetters:
                inputLetters += newLetter.text.lower() + ", "
                if newLetter.text.lower() not in selectedWord:
                    lives -= 1
                    text += '? La letra no está en la palabra. Te quedan ' + str(lives) + ' intentos.' + '\n'
                else:
                    text += '? Letra correcta!' + '\n'
            else:
                text += '? Letra repetida!' + '\n'
        else:
            text += '? Por favor, solo una letra en cada mensaje.' + '\n'
    else:
        text += '? Vaya, esto no es lo que esperaba...'
    play_hangman(text, lives, selectedWord, clue, inputLetters, bot, message)