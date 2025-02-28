import os
import discord
import requests
import asyncio

from bs4 import BeautifulSoup
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv, set_key
from datetime import datetime

env_directorio = "bot.env"
load_dotenv(env_directorio)

TOKEN = os.getenv('DISCORD_TOKEN')
LINK_MATERIAS = os.getenv('LINK_MATERIAS')
LINK_FINALES = os.getenv('LINK_FINALES')
FECHA_MATERIAS = os.getenv('MATERIAS_FECHA_GUARDADA')
FECHA_FINALES = os.getenv('FINALES_FECHA_GUARDADA')
UNGS_LINK = 'https://www.ungs.edu.ar/estudiar-en-la-ungs/inscripciones/oferta-academica-mesas-de-examen'

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN no encontrado en archivo .env.")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents = discord.Intents.all())

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

async def fetch_pdf_link(keyword):
    global UNGS_LINK
    try:
        response = requests.get(UNGS_LINK)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            link_tag = soup.find('a', href=lambda href:href and keyword in href)

            if link_tag:
                href = link_tag['href']
                print("Link al PDF:", href)
                return href
            else: 
                return None
        else:
            print(f"No se encontró la página.")
    except requests.RequestException as e:
        print(f"Error buscando PDF: {e}")
        return None
            
async def chequearOferta(keyword: str):
    global LINK_MATERIAS, FECHA_MATERIAS, LINK_FINALES, FECHA_FINALES
    
    links = {
        "Publicacion-Materias": {"link": LINK_MATERIAS, "fecha": FECHA_MATERIAS, "env_key": "LINK_MATERIAS", "date_key": "MATERIAS_FECHA_GUARDADA"},
        "MESAS-DE-EXAMEN": {"link": LINK_FINALES, "fecha": FECHA_FINALES, "env_key": "LINK_FINALES", "date_key": "FINALES_FECHA_GUARDADA"}
    }
    
    if keyword not in links:
        print(f"Keyword '{keyword}' no válido.")
        return
        
    nuevoLink = await fetch_pdf_link(keyword)
    
    if not nuevoLink:
        print(f"No se encontró el archivo.")
        return
    
    link_info = links[keyword]
    
    id_canal_notificar = get_id_canal()
    canal = get_channel_by_id(bot, id_canal_notificar) if id_canal_notificar else None
    
    if nuevoLink != link_info["link"]:
        if (keyword == "Publicacion-Materias"):
            mensaje = f'@everyone ¡El PDF de Oferta Académica fue actualizado! Aquí está el nuevo enlace: {nuevoLink}. No olvides anotarte antes que se termine el llamado~'
        elif (keyword == "MESAS-DE-EXAMEN"):
            mensaje = f'@everyone ¡El pdf de las Mesas de Examen fue actualizado! Aquí está el nuevo enlace: {nuevoLink}.'

        if canal:
            link_info["link"] = nuevoLink
            fecha_actual = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            link_info["fecha"] = fecha_actual

            set_key('bot.env', link_info["env_key"], nuevoLink)
            set_key('bot.env', link_info["date_key"], fecha_actual)

            print(f'El link almacenado era distinto al de la página web, el nuevo link se ha almacenado!')
            await canal.send(mensaje)
        else:
            print("El ID del canal no ha sido seteado aún! Usa el comando '@{bot.user} set_channel' para setear el ID.")
    else:
        print(f'El link almacenado tiene la última versión.')
        if canal:
            await canal.send(f'El link almacenado tiene la última versión. Usa /ultimoLink para ver los links a las materias.')
    
@bot.event
async def on_ready():
    print(f'Bot is up and ready!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} comandos sincronizados")
    except Exception as e:
        print(f" Error al sincronizar comandos: {e}")
        
    await chequearOferta("Publicacion-Materias")
    await chequearOferta("MESAS-DE-EXAMEN")

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f"Hola {member.name}, bienvenido al servidor! Como aviso, tenemos un canal notificacion-inscripcion donde recibirás notificaciones semestrales cuando sea fecha de inscripción por mi parte. Espero que te diviertas, y si te molesto mucho puedes mutear el canal.")
        
@bot.tree.command(name="setcanal", description="Setea el canal donde el bot enviará los mensajes")
async def set_channel(interaction: discord.Interaction, id_canal: discord.TextChannel):
    setear_id_canal(id_canal.id)
    await interaction.response.send_message(f"{interaction.user.mention} el canal {id_canal.mention} se ha seteado. Los mensajes se enviarán a este canal.", ephemeral=True)

@bot.tree.command(name="chequearoferta", description="Verifica que el calendario de oferta académica esté al día")
async def chequearOfertaAcademica(interaction: discord.Interaction):
    await chequearOferta("Publicacion-Materias")
    await interaction.response.send_message("Chequeo de calendario de Materias exitoso.", ephemeral=True)
    
@bot.tree.command(name="chequearfinales", description="Verifica que el calendario de mesa de examen esté al día")
async def chequearFinal(interaction: discord.Interaction):
    await chequearOferta("MESAS-DE-EXAMEN")
    await interaction.response.send_message("Chequeo de calendario de Finales exitoso.", ephemeral=True)

@bot.tree.command(name="ultimolink", description="¡Te muestra el último link que tiene guardado al bot sin pingear a todos en el server!")
async def ultimoRegistro(interaction: discord.Interaction):
    await interaction.response.send_message(f'{interaction.user.mention} la última versión que poseo de la Oferta Académica es del: {FECHA_MATERIAS}, y el link es: {LINK_MATERIAS}.\nLa última versión que poseo de las Mesas de Examen es: {FECHA_FINALES}, y el link es: {LINK_FINALES}.')

bot.run(TOKEN)

