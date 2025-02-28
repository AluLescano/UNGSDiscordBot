# UNGSDiscordBot
`Bot para el chequeo del calendario académico y posteo automatizado en un servidor de Discord.`

Este bot fue un proyecto para la universidad utilizando su plataforma para buscar y extraer los links de las ofertas de examen y materias de cada semestre con el fin de compartir los links a través del servidor de la comunidad de la carrera de programación para acceder a ellos de manera rápida. El bot sigue creciendo con el paso del tiempo y se le van agregando nuevas funcionalidades, como por ejemplo el proveer información de contacto de la universidad por medio de los `comandos slash (/)` que permite Discord.

Se utilizaron las librerías BeautifulSoup y Pycord para poder encontrar los links por medio de palabras clave y entregarlos a través de la plataforma. Además, el bot utiliza un archivo .env

>[!IMPORTANT]
> El archivo .env fue excluido de los commits ya que posee información delicada como el Token del Bot de Discord, el ID del Servidor, Información de Contacto entre otros.
> Se requiere crear el archivo .env correspondiente para que el código se ejecute de manera correcta.

>[!IMPORTANT]
> Para que el bot funcione correctamente se debe crear una "APP" a través del [Discord Developer Portal](https://discord.com/developers/applications/) donde además de otorgarle permisos, obtienes tu Token.

En la última versión disponible se modificó el código de manera que fuera más eficiente y no tuviese redundancia en la misma. 
