import os
import discord
import requests
import asyncio

from bs4 import BeautifulSoup
from dotenv import load_dotenv, set_key
from discord.ext import commands
from datetime import datetime

# Cargo las variables desde el archivo .env
env_directorio = "bot.env"
load_dotenv(env_directorio)

# Accedo a esas variables usando os.environ.get()
TOKEN = os.environ.get('DISCORD_TOKEN')
LINK_MATERIAS = os.environ.get('LINK_MATERIAS')
LINK_FINALES = os.environ.get('LINK_FINALES')
FECHA_MATERIAS = os.environ.get('MATERIAS_FECHA_GUARDADA')
FECHA_FINALES = os.environ.get('FINALES_FECHA_GUARDADA')
UNGS_LINK = 'https://www.ungs.edu.ar/estudiar-en-la-ungs/inscripciones/oferta-academica-mesas-de-examen'

# Me aseguro que el token existe
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no encontrado en archivo .env.")

# Seteo los permisos requeridos para el bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Pasamos los intents al bot
bot = commands.Bot(command_prefix=commands.when_mentioned_or('/'), intents=intents)

def setear_id_canal(id_canal):
    # Funcion para setear la nueva ID del canal en el archivo env
    # Convierto el ID a String
    id_canal_str = str(id_canal)
    set_key('bot.env', 'ID_CANAL', id_canal_str)

def get_id_canal():
    # Funcion para leer el ID del canal a través del .env
    id_canal_str = os.environ.get('ID_CANAL', '0')
    if id_canal_str:
        return int(id_canal_str)
    else:
        return 0

def get_channel_by_id(client, id_canal):
    for guild in client.guilds:
        canal = guild.get_channel(id_canal)
        if canal:
            return canal
    return None

async def chequearActualizacion(TEXT):
    global UNGS_LINK  # Declaro UNGS_LINK como variable global
    response = requests.get(UNGS_LINK)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Defino funcion para chequear si la página tiene el string recibido
        def tiene_palabra(string):
            return string and TEXT in string

        # Uso la funcion soup.find() para obtener la etiqueta anchor
        link_tag = soup.find('a', string=tiene_palabra)

        # Si encuentra el link, obtiene el atributo href para el .pdf
        if link_tag:
            href = link_tag['href']
            print("Link al PDF: ", href)

            return href

        else:
            print(f'Link no encontrado.')

    else:
        print(f'Fallo al buscar la página web.')

async def chequearOferta():
    global LINK_MATERIAS  # Declaro LINK_MATERIAS como variable global
    texto = 'Ver Oferta Académica'
    NuevoLink = ''
    NuevoLink = await chequearActualizacion(texto)

    id_canal_notificar = get_id_canal()
    if id_canal_notificar != 0:
        canal = get_channel_by_id(bot, id_canal_notificar)

    if NuevoLink != LINK_MATERIAS:
        # Envia un mensaje al canal indicado para indicar que se actualizó el archivo
        mensaje = f'@everyone ¡El pdf de Oferta Académica fue actualizado! Aquí está el nuevo enlace: {NuevoLink}. No olvides anotarte antes que se termine el llamado de este semestre~ (Este mensaje puede reenviarse varias veces, depende de la cantidad de actualizaciones que hagan durante las fechas de inscripción.)'

        if canal:
            LINK_MATERIAS = NuevoLink
            fecha_actual = datetime.now()

            formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")

            set_key('bot.env', 'LINK_MATERIAS', LINK_MATERIAS)  # Guardo el valor en el archivo .env
            set_key('bot.env', 'MATERIAS_FECHA_GUARDADA', formatofecha)  # Guardo el valor en el archivo .env

            print(f'El link almacenado era distinto al de la página web, el nuevo link se ha almacenado!')
            await canal.send(mensaje)

        else:
            print("El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")

    else:
        print(f'El link almacenado tiene la última versión.')
        fecha_actual = datetime.now()

        formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")
        set_key('bot.env', 'MATERIAS_FECHA_GUARDADA', formatofecha)  # Guardo el valor en el archivo .env
        if canal: 
            await canal.send(f"La última versión del calendario es la siguiente: {LINK_MATERIAS}.")
        else:
            print ("Hubo un error al intentar enviar el mensaje al canal.")

async def chequearFinal():
    global LINK_FINALES  # Declaro LINK_FINALES como variable global
    texto = 'Ver Mesas de Examen'
    NuevoLink = ''
    NuevoLink = await chequearActualizacion(texto)

    id_canal_notificar = get_id_canal()
    if id_canal_notificar != 0:
        canal = get_channel_by_id(bot, id_canal_notificar)

    if NuevoLink != LINK_FINALES:
        # Envia un mensaje al canal indicado para indicar que se actualizó el archivo
        mensaje = f'@everyone ¡El pdf de las Mesas de Examen fue actualizado! Aquí está el nuevo enlace: {NuevoLink}.)'

        if canal:
            LINK_FINALES = NuevoLink
            fecha_actual = datetime.now()

            formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")

            set_key('bot.env', 'LINK_FINALES', LINK_FINALES)  # Guardo el valor en el archivo .env
            set_key('bot.env', 'FINALES_FECHA_GUARDADA', formatofecha)  # Guardo el valor en el archivo .env

            print(f'El link almacenado era distinto al de la página web, el nuevo link se ha almacenado!')
            await canal.send(mensaje)

        else:
            print("El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")
            #await .send(f"El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")
    else:
        print(f'El link almacenado tiene la última versión.')
        fecha_actual = datetime.now()

        formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")
        set_key('bot.env', 'FINALES_FECHA_GUARDADA', formatofecha)  # Guardo el valor en el archivo .env
        if canal: 
            await canal.send(f"La última versión del calendario es la siguiente: {LINK_FINALES}.")
        else:
            print ("Hubo un error al intentar enviar el mensaje al canal.")

@bot.event
async def on_ready():
    print(f'{bot.user} se ha conectado a Discord!')
    await chequearOferta()
    await chequearFinal()

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hola {member.name}, bienvenido al servidor! Como aviso, tenemos un canal notificacion-inscripcion donde '
        f'recibirás notificaciones semestrales cuando sea fecha de inscripción por mi parte. Espero que te '
        f'diviertas, y si te molesto mucho puedes mutear el canal.'
    )

@bot.command()
async def set_channel(ctx, id_canal: discord.TextChannel):
    # Comando para setear el canal en lugar del ID
    setear_id_canal(id_canal.id)
    await ctx.send(f'El canal {id_canal.mention} se ha seteado. Los mensajes se enviarán a este canal.')

@bot.command()
async def chequearMaterias(ctx):
    # Comando para manualmente chequear una actualización del pdf del calendario
    await chequearOferta()
    await ctx.send('Chequeo de calendario de Materias exitoso.')

@bot.command()
async def chequearFinales(ctx):
    # Comando para manualmente chequear una actualización del pdf del calendario
    await chequearFinal()
    await ctx.send('Chequeo de calendario de Finales exitoso.')

@bot.command()
async def ultimoRegistro(ctx):
    # Comando para obtener la última versión del pdf sin pinguear a todos
    await ctx.send(f'El último registro de Oferta Académica es: {FECHA_MATERIAS}, y el link es: {LINK_MATERIAS}. '
                   f'El último registro de Mesas de Examen es: {FECHA_FINALES}, y el link es: {LINK_FINALES}.')

bot.run(TOKEN)

