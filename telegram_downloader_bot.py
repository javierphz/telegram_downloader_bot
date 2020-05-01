################################################################################
#
# Fast & Dirty telegram downloader bot.
#
#    Just for fun and learning purposes.
#
#    2020 Fco. Javier P.H
#
###############################################################################

from telethon import TelegramClient, events, Button
import logging
import sys
import datetime
from os import listdir
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',level=logging.WARNING)

# Use your own values from my.telegram.org
api_id = 00000000 # fill it with your id
api_hash = 'your hash will be here'
bot_token = 'your bot token will be here'
DOWNLOADS_DIR="./telegram_downloads/"

current_download = ["",0,0,0,datetime.datetime.now()]
download_queue = []
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

def now():
    return datetime.datetime.now().replace(microsecond=0).isoformat()

@bot.on(events.NewMessage(pattern='/quit'))
async def start(event):
    print("[I] [" + now() + "] Command /quit received")
    await event.respond('Quitting!')
    raise events.StopPropagation
    sys.exit("/quit message")

@bot.on(events.NewMessage(pattern='/help'))
async def start(event):
    print("[I] [" + now() + "] Command /help received")
    await event.respond('Reenvia aquí el fichero que quieres descargar\n **Comandos:**\n  /help: Esta respuesta\n  /estado: información del estado actual\n  /cola [borrar indice]: muestra la cola o borra el elemento con el indice indicado\n  /ls: lista el contenido del directorio de descargas')
    raise events.StopPropagation
    sys.exit("/quit message")

@bot.on(events.NewMessage(pattern='/estado'))
async def start(event):
    """Send a message when the command /start is issued."""
    print("[I] [" + now() + "] Command /estado received")
    response = "Descarga activa: "

    if current_download[0] == "":
        response += "**Ninguna!**\n"
    else:
        response += "\n**" + str(current_download[0]) +  '**\n[ **{:.2f}%**'.format((current_download[2] / current_download[1])*100) + " - " + '**{:.2f} Kb/s** ]\n'.format(current_download[3])

    response += "Encolados: **{}**".format(len(download_queue))

    await event.respond(response)
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='\/cola( (borrar) ([0-9]{1,2})){0,1}$'))
async def start(event):
    print("[I] [" + now() + "] Command /cola received")

    if len(download_queue) != 0:
        response = ""

        if (event.pattern_match.group(2) == "borrar"):
            n = int(event.pattern_match.group(3))
            if (n < len(download_queue)):
                file_name = download_queue[n].file.name
                download_queue.pop(n)
#                await event.respond('Yes or no?', buttons=[Button.inline('Yes!', b'yes'), Button.inline('Nope', b'no')])
                print("[I] [{}] {} deleted!".format(now(),file_name))
                await event.respond('Borrado elemento **' + file_name + "** ! ")
            else:
                print("[I] [" + now() + "] Wrong format for /cola command")
                await event.respond('Posición **{}** no válida!'.format(n))
        else:

            response += '**--- Cola ---**\n'

            for i in range(0,len(download_queue)):
                sender = await download_queue[i].get_sender()
                response += "**{}** : [**@{}**] {}\n".format(i,sender.username,download_queue[i].file.name)

            await event.respond(response)

    else:
        await event.respond('¡Cola Vacia!')

    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/ls$'))
async def start(event):
    print("[I] [" + now() + "] Command /ls received")

    response = ""
    for f in listdir(DOWNLOADS_DIR):
        response += f + "\n"

    if len(response) != 0:
        await event.respond(response)

    else:
        await event.respond('Directorio vacio.')

    raise events.StopPropagation

def callback(current, total):
    current_download[1] = total
    current_download[2] = current
    secs = (datetime.datetime.now() - current_download[4]).total_seconds()
    current_download[3] = current / (secs * 1024)

@bot.on(events.NewMessage)
async def echo(event):
    """Echo the user message."""
    print("[I] [" + now() + "] New message received")
    if event.media != None:

        if current_download[0] == "":
            print("[I] [" + now() + "] No current download active. Downloading " + event.file.name)
            ev = event
            while True:
                current_download[0] = ev.file.name
                current_download[4] = datetime.datetime.now()
                await ev.respond("**Descargando **" + ev.file.name + " ... ")
                print("[I] [" + now() + "] Downloading " + ev.file.name + " ... ")
                await bot.download_media(ev.message,DOWNLOADS_DIR+"/"+ev.file.name,progress_callback=callback)
                print("[I] [" + now() + "] Downloaded " + ev.file.name + " !")
                await ev.respond("**Descargado** " + ev.file.name + "!")
                #raise ev.StopPropagation

                if len(download_queue) == 0:
                    current_download[0] = ""
                    break;
                else:
                    ev = download_queue.pop(0)
        else:
            if len(download_queue) <= 10:
                download_queue.append(event)
                print("[I] [" + now() + "] Queued!")
                await event.respond("**Encolado.**")
            else:
                print("[I] [" + now() + "]  Full Queue!")
                await event.respond("**¡Cola llena!**")

    else:
        print("[I] [" + now() + "] No media or wrong command")
        await event.respond("**Mensaje sin contenido multimedia para descargar o comando no válido!** /help para más información")

def main():
    """Start the bot."""
    print("[I] [" + now() + "] Starting bot")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
