#Ahorcado
from config import *    #importamos el token
import telebot  #para manejar la API de Telegram
from telebot.types import ReplyKeyboardMarkup   #botones y demás
from telebot.types import ForceReply    #citar un mensaje
import random

def imprimirAhorcado(vidas):
    text = '_____' + '\n'
    text += '|        |' + '\n'
    if vidas == 6:        
        text += '|' + '\n'
        text += '|' + '\n'
        text += '|' + '\n'
    elif vidas == 5:
        text += '|      😵' + '\n'
        text += '|' + '\n'
        text += '|' + '\n'
    elif vidas == 4:
        text += '|      😵' + '\n'
        text += '|       |' + '\n'
        text += '|' + '\n'
    elif vidas == 3:
        text += '|      😵' + '\n'
        text += '|      /|' + '\n'
        text += '|' + '\n'
    elif vidas == 2:
        text += '|      😵' + '\n'
        text += '|      /|\ ' + '\n'
        text += '|' + '\n'
    elif vidas == 1:
        text += '|      😵' + '\n'
        text += '|      /|\ ' + '\n'
        text += '|      /' + '\n'
    elif vidas == 0:
        text += '|      😵' + '\n'
        text += '|      /|\ ' + '\n'
        text += '|      / \ ' + '\n'
    text += '| _____' + '\n'
    return text
        
def textoInicial(bot):
    photo = open("ahorcado.png", "rb")
    text = '<b><u>Bienvendi@ al juego del Ahorcado o Hangman.</u></b>' + '\n'
    text += 'Introduce letras para adivinar la palabra oculta antes de que se te acaben los intentos.'
    msg = bot.send_photo(MY_CHAT_ID, photo, text, parse_mode='html')

#MAIN
def jugar(bot):
    textoInicial(bot)
    palabras = ["abanico", "elefante", "jardinero", "sobaco", "chocolate", "lluvia"]
    idPalabraElegida = random.randint(0, len(palabras)-1)
    palabraElegida = palabras[idPalabraElegida]
    print (palabraElegida)
    palabrasEjercicio = ""
    vidas = 6
    text = ''
    while vidas > 0:
        fallas = 0
        text += imprimirAhorcado(vidas) + '\n'
        text += '✰ Palabra a adivinar: '
        for letra in palabraElegida:
            if letra in palabrasEjercicio:
                text += letra
            else:
                text += '_ '
                fallas += 1
        if fallas == 0:
            #imprimirAhorcado(bot, vidas, text)
            text = '#############################' + '\n'
            text += '#  🥳 FELICIDADES, HAS GANADO 🥳  #' + '\n'
            text += '#############################'
            msg = bot.send_message(MY_CHAT_ID, text, parse_mode='html')
            break
        text += '\n' + '✰ Letras ya introducidas:' + palabrasEjercicio + '\n'
        msg = bot.send_message(MY_CHAT_ID, text, parse_mode='html')
        markup = ForceReply()
        letraIntroducida = bot.send_message(MY_CHAT_ID, "✰ Introduce una letra: ", reply_markup=markup)
        bot.register_next_step_handler(letraIntroducida, nuevaLetra, palabrasEjercicio)
        
        if letraIntroducida.text not in palabraElegida:
            vidas -= 1
            text = '* La letra no está en la palabra. Te quedan ' + str(vidas) + ' intentos.' + '\n' + '\n'
            
        if vidas == 0:
            text = 'Lo siento, has perdido 😥' + '\n' + '\n'
            text += imprimirAhorcado(vidas) + '\n'
            text += '* La palabra era: ' + palabraElegida 
            msg = bot.send_message(MY_CHAT_ID, text, parse_mode='html')
            
def nuevaLetra(letraIntroducida, palabrasEjercicio):
    palabrasEjercicio += letraIntroducida.text
    
    