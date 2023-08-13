# Bot_cumples_telegram

Este código corresponde a la programación de un chatbot multifunción de Telegram.

Este bot es capaz de recordar o felicitar los cumpleaños almacenados en la base de datos, moderar grupos detectando algunas palabras consideradas como inapropiadas y jugar al ahorcado.

## Modificaciones en el código
Para su correcta ejecución han de añadirse un par de modificaciones en los siguientes ficheros:
- **config.py:** Deben darse valor a las variables *TELEGRAM_TOKEN* y *MY_CHAT_ID*. La primera corresponde al token del bot, este token se consigue cuando se crea el bot en el chat con Bot Father en Telegram. Debe ser un *String*, luego debe ir entre comillas. Por otro lado, la segunda es un *int* y corresponde al id del creador o dueño del bot. Permite tener privilegios en algunos comandos. Este id puede conseguirse escribiendo *print(message.from_user.id)* en cualquier método correspondiente a un comando, por ejemplo en el de *cmd_start*, así, una vez ejecutado el bot, si se escribe en su chat el comando */start*, se mostrará en la terminal el id del usuario que envío el mensaje. Si en lugar de verlo mostrado en la terminal se desea ver en el chat del bot, se debe añadir *bot.send_message(message.chat.id, message.from_user.id)*.
- **fun_mod.py:** En el método *connect_db* han de darse valor a las variables *host*, *port*, *user*, *password* y *database* correspondiente con las del servidor de base de datos donde se vayan a realidar las consultas y guardar la información que recolecte el bot.

## Creación de la base de datos
Por otro lado, también ha de construirse una base de datos SQL con la correspondiente estructura para que las consultas se puedan llevar a cabo correctamente:

![Imagen del diagrama entidad relación que debe seguir la base de datos](https://github.com/eleeeena1204/Bot_cumples_telegram/blob/main/Diagrama%20entidad%20relación.png)

Las únicas tablas que deben tener contenido previo son *swearwords* y *hangmanwords* ya que son bancos de palabras. El primero debe contener aquellas palabras que se consideren inapropiadas y que si un usuario de un grupo las escribe, recibirá hasta 2 avisos y al tercero será baneado del grupo. En la segunda tabla deben añadirse las palabras que se consideren apropiadas para ser palabras ocultas en el juego del ahorcado.

## Ejecución del bot
Una vez descargados los archivos de este repositorio, creada la base de datos y realizados los cambios mencionados, para poner en ejecución el bot ha de hacerse desde la consola. Se debe ingresar desde la consola al directorio donde se encuentren todos los ficheros y, con Python3 instalado, se debe introducir en la terminal el comando *python bot_telegram.py* o, si tiene más de una versión de python instalada, el comando *python3 bot_telegram.py*. Se mostrará un mensaje indicando que el bot ha sido iniciado y ya podrá empezar una conversación con él por privado, agregarlo a grupos y hablar por el grupo en el que ya esté incluida. 

Es importante que para que el bot pueda banear a usuarios, se le den permisos de administrador en el grupo a la hora de ser añadido a uno.
