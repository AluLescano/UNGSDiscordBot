import os
import discord
import requests
import asyncio

from bs4 import BeautifulSoup
from dotenv import load_dotenv, set_key
from discord.ext import commands
from datetime import datetime

#Cargo las variables desde el archivo .env
load_dotenv("bot.env")

#Accedo a esas variables usando os.environ.get()
TOKEN = os.environ.get('DISCORD_TOKEN')
LINK_CALENDARIO = os.environ.get('LINK_CALENDARIO')
FECHA = os.environ.get('FECHA_GUARDADA')

#Me aseguro que el token existe
if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no encontrado en archivo .env.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or('/'), intents=intents)  # Pasamos los intents al bot

def setear_id_canal(id_canal):
    # Convert the integer ID to a string
    id_canal_str = str(id_canal)
    # Funcion para setear la nueva ID del canal en el archivo de configuración
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
		return none
    
async def revisar_actualizacion_calendario():
    global LINK_CALENDARIO  # Declaro LINK_CALENDARIO como variable global

    url = 'https://www.ungs.edu.ar/estudiar-en-la-ungs/inscripciones/oferta-academica-mesas-de-examen'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Defino funcion para chequear si la etiqueta tiene "Ver Oferta Académica"
        def tiene_oferta(string):
            return string and "Ver Oferta Académica" in string

        # Uso la funcion soup.find() para obtener la etiqueta anchor
        link_tag = soup.find('a', string=tiene_oferta)

        # Si encuentra el link, obtiene el atributo href para el .pdf
        if link_tag:
            href = link_tag['href']
            print("Link al PDF de la Oferta Académica: ", href)

            # Envia un mensaje al canal indicado para indicar que se actualizó el archivo
            id_canal_notificar = get_id_canal()
            
            if id_canal_notificar != 0:
                mensaje = f'¡El pdf de Oferta Académica fue actualizado! Aquí está el nuevo enlace: {href}. No olvides anotarte antes que se termine el llamado de este semestre~ (Este mensaje puede reenviarse varias veces, depende de la cantidad de actualizaciones que hagan durante las fechas de inscripción.)'
                canal = get_channel_by_id(bot, id_canal_notificar)
                
                if canal:
                    if href != LINK_CALENDARIO:
                        LINK_CALENDARIO = href
                        fecha_actual = datetime.now()
                        
                        formatofecha = fecha_actual.strftime("%d-%m-%Y %H:%M:%S")
                        
                        set_key('bot.env', 'LINK_CALENDARIO', LINK_CALENDARIO)  # Guardo el valor en el archivo .env
                        set_key('bot.env', 'FECHA_GUARDADA', formatofecha)  # Guardo el valor en el archivo .env
                        
                        print(f'El link almacenado era distinto al de la página web, el nuevo link se ha almacenado!')
                        await canal.send(mensaje)
                    else:
                        print(f'El link almacenado tiene la última versión.')
                        await canal.send(f"La última versión del calendario es la siguiente: {LINK_CALENDARIO}")
            else:
                print("El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")
                #await .send(f"El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")
        else:
            print(f'Link no encontrado.')
            #await ctx.send(f"Hubo un fallo al encontrar el link, por favor contacta a Alu si encuentras este problema")
    else:
        print(f'Fallo al buscar la página web.')
        #await ctx.send(f"Hubo un fallo al encontrar el link, por favor contacta a Alu si encuentras este problema")


@bot.event
async def on_ready():
    print(f'{bot.user} se ha conectado a Discord!')
    await revisar_actualizacion_calendario()

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
async def chequear_actualizacion(ctx):
    # Comando para manualmente chequear una actualización del pdf del calendario
    await revisar_actualizacion_calendario()
    await ctx.send('Chequeo de calendario exitoso.')
    
@bot.command()
async def get_link(ctx):
	# Comando para obtener la ultima versión del pdf sin pinguear a todos
	await ctx.send(f'El último registro que tengo del calendario académico es: {FECHA}, Y el link es este: {LINK_CALENDARIO}')


bot.run(TOKEN)

