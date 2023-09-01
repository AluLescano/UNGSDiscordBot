import os
import discord
import requests
import asyncio

from bs4 import BeautifulSoup
from dotenv import load_dotenv, set_key
from discord.ext import commands
from datetime import datetime

env_directorio = "bot.env"
load_dotenv(env_directorio)

TOKEN = os.environ.get('DISCORD_TOKEN')
LINK_MATERIAS = os.environ.get('LINK_MATERIAS')
LINK_FINALES = os.environ.get('LINK_FINALES')
FECHA_MATERIAS = os.environ.get('MATERIAS_FECHA_GUARDADA')
FECHA_FINALES = os.environ.get('FINALES_FECHA_GUARDADA')
UNGS_LINK = 'https://www.ungs.edu.ar/estudiar-en-la-ungs/inscripciones/oferta-academica-mesas-de-examen'

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no encontrado en archivo .env.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('/'), intents=intents)

def setear_id_canal(id_canal):
    id_canal_str = str(id_canal)
    set_key('bot.env', 'ID_CANAL', id_canal_str)

def get_id_canal():
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
    global UNGS_LINK
    response = requests.get(UNGS_LINK)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        def tiene_palabra(string):
            return string and TEXT in string

        link_tag = soup.find('a', string=tiene_palabra)

        if link_tag:
            href = link_tag['href']
            print("Link al PDF:", href)
            return href
        else:
            print(f'Link no encontrado.')
    else:
        print(f'Fallo al buscar la página web.')

async def chequearOferta():
    global LINK_MATERIAS
    global FECHA_MATERIAS
    
    texto = 'Ver Oferta Académica'
    NuevoLink = ''
    NuevoLink = await chequearActualizacion(texto)

    id_canal_notificar = get_id_canal()
    if id_canal_notificar != 0:
        canal = get_channel_by_id(bot, id_canal_notificar)

    if NuevoLink != LINK_MATERIAS:
        mensaje = f'@everyone ¡El pdf de Oferta Académica fue actualizado! Aquí está el nuevo enlace: {NuevoLink}. No olvides anotarte antes que se termine el llamado de este semestre~ (Este mensaje puede reenviarse varias veces, depende de la cantidad de actualizaciones que hagan durante las fechas de inscripción.)'

        if canal:
            LINK_MATERIAS = NuevoLink
            fecha_actual = datetime.now()

            formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")
            FECHA_MATERIAS = formatofecha

            set_key('bot.env', 'LINK_MATERIAS', LINK_MATERIAS)
            set_key('bot.env', 'MATERIAS_FECHA_GUARDADA', FECHA_MATERIAS)

            print(f'El link almacenado era distinto al de la página web, el nuevo link se ha almacenado!')
            await canal.send(mensaje)
        else:
            print("El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")
    else:
        print(f'El link almacenado tiene la última versión.')
        fecha_actual = datetime.now()

        formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")
        FECHA_MATERIAS = formatofecha

        set_key('bot.env', 'MATERIAS_FECHA_GUARDADA', FECHA_MATERIAS)
        if canal: 
            await canal.send(f"La última versión del calendario es la siguiente: {LINK_MATERIAS}.")
        else:
            print ("Hubo un error al intentar enviar el mensaje al canal.")

async def chequearFinal():
    global LINK_FINALES
    global FECHA_FINALES
    texto = 'Ver Mesas de Examen'
    NuevoLink = ''
    NuevoLink = await chequearActualizacion(texto)

    id_canal_notificar = get_id_canal()
    if id_canal_notificar != 0:
        canal = get_channel_by_id(bot, id_canal_notificar)

    if NuevoLink != LINK_FINALES:
        mensaje = f'@everyone ¡El pdf de las Mesas de Examen fue actualizado! Aquí está el nuevo enlace: {NuevoLink}.)'

        if canal:
            LINK_FINALES = NuevoLink
            fecha_actual = datetime.now()

            formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")
            FECHA_FINALES = formatofecha

            set_key('bot.env', 'LINK_FINALES', LINK_FINALES)
            set_key('bot.env', 'FINALES_FECHA_GUARDADA', FECHA_FINALES)

            print(f'El link almacenado era distinto al de la página web, el nuevo link se ha almacenado!')
            await canal.send(mensaje)
        else:
            print("El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")
    else:
        print(f'El link almacenado tiene la última versión.')
        fecha_actual = datetime.now()
        	
        formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")
        FECHA_FINALES = formatofecha
        
        set_key('bot.env', 'FINALES_FECHA_GUARDADA', FECHA_FINALES)
        if canal: 
            await canal.send(f"La última versión de la oferta a finales es la siguiente: {LINK_FINALES}.")
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
    setear_id_canal(id_canal.id)
    await ctx.send(f'El canal {id_canal.mention} se ha seteado. Los mensajes se enviarán a este canal.')

@bot.command()
async def chequearMaterias(ctx):
    await chequearOferta()
    await ctx.send('Chequeo de calendario de Materias exitoso.')

@bot.command()
async def chequearFinales(ctx):
    await chequearFinal()
    await ctx.send('Chequeo de calendario de Finales exitoso.')

@bot.command()
async def ultimoRegistro(ctx):
    await ctx.send(f'La última versión que poseo de la Oferta Académica es: {FECHA_MATERIAS}, y el link es: {LINK_MATERIAS}. La última versión que poseo de las Mesas de Examen es: {FECHA_FINALES}, y el link es: {LINK_FINALES}.')

bot.run(TOKEN)

