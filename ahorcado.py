#Ahorcado
import random
palabras = ["abanico", "elefante", "jardinero", "sobaco", "chocolate", "lluvia"]
idPalabraElegida = random.randint(0, len(palabras)-1)
palabraElegida = palabras[idPalabraElegida]
print (palabraElegida)
palabraEjercicio = ""
vidas = 6

def imprimirAhorcado():
    if vidas == 6:
        print ("           ___")
        print ("          |   |")
        print ("              |")
        print ("              |")
        print ("              |")
        print ("          ____|")
    elif vidas == 5:
        print ("           ___")
        print ("          |   |")
        print ("          O   |")
        print ("              |")
        print ("              |")
        print ("          ____|")
    elif vidas == 4:
        print ("           ___")
        print ("          |   |")
        print ("          O   |")
        print ("          |   |")
        print ("              |")
        print ("          ____|")
    elif vidas == 3:
        print ("           ___")
        print ("          |   |")
        print ("          O   |")
        print ("         /|   |")
        print ("              |")
        print ("          ____|")
    elif vidas == 2:
        print ("           ___")
        print ("          |   |")
        print ("          O   |")
        print ("         /|\  |")
        print ("              |")
        print ("          ____|")
    elif vidas == 1:
        print ("           ___")
        print ("          |   |")
        print ("          O   |")
        print ("         /|\  |")
        print ("         /    |")
        print ("          ____|")
    elif vidas == 0:
        print ("           ___")
        print ("          |   |")
        print ("          O   |")
        print ("         /|\  |")
        print ("         / \  |")
        print ("          ____|")
        
def textoInicial():
    print ("")
    print ("*************************************************************************************")
    print ("*                                                                                   *")
    print ("*     ##      ##   ##    #####    ######      ####      ##      #####      #####    *")
    print ("*    ####     ##   ##   ##   ##    ##  ##    ##  ##    ####      ## ##    ##   ##   *")
    print ("*   ##  ##    ##   ##   ##   ##    ##  ##   ##        ##  ##     ##  ##   ##   ##   *")
    print ("*   ##  ##    #######   ##   ##    #####    ##        ##  ##     ##  ##   ##   ##   *")
    print ("*   ######    ##   ##   ##   ##    ## ##    ##        ######     ##  ##   ##   ##   *")
    print ("*   ##  ##    ##   ##   ##   ##    ##  ##    ##  ##   ##  ##     ## ##    ##   ##   *")
    print ("*   ##  ##    ##   ##    #####    #### ##     ####    ##  ##    #####      #####    *")
    print ("*                                                                                   *")
    print ("*************************************************************************************")
    print ("")
    print ("Bienvendi@ al juego del Ahorcado o Hangman.")
    print ("Introduce letras para adivinar la palabra oculta antes de que se te acaben los intentos.")

#MAIN
def jugar():
    textoInicial()
    while vidas > 0:
        fallas = 0
        print ("")
        imprimirAhorcado()
        print ("")
        print ("* Palabra a adivinar: ", end = "")
        for letra in palabraElegida:
            if letra in palabraEjercicio:
                print (letra, end="")
            else:
                print ("_", end = "")
                fallas+=1
        if fallas == 0:
            print ("")
            imprimirAhorcado()
            print ("")
            print ("#############################")
            print ("#  FELICIDADES, HAS GANADO  #")
            print ("#############################")
            break
          
        print ("")
        print ("* Letras ya introducidas:", palabraEjercicio)
        letraIntroducida = input ("* Introduce una letra: ")
        palabraEjercicio+=letraIntroducida
        
        if letraIntroducida not in palabraElegida:
            vidas -= 1
            print ("* La letra no está en la palabra. Te quedan ", vidas, " intentos.")
            
        if vidas == 0:
            imprimirAhorcado()
            print ("")
            print ("############################")
            print ("#  LO SIENTO, HAS PERDIDO  #")
            print ("############################")
            print ("")
            print ("* La palabra era: ", palabraElegida)