import re
import discord
from messageBox import messageBox
from memberProp import DiscordMember
from settings import BOT_TOKEN, SERVER_ID
from integrations import integrity_checks, notify_un_verified, un_register_member


intents = discord.Intents.all()
client = discord.Client(intents=intents)
SERVER = None
ROLES = dict()  # cache the role objects
bunker = dict()  # cache discord incomplete details


@client.event
async def on_ready():
    global SERVER, ROLES
    SERVER = discord.utils.get(client.guilds, id=SERVER_ID)
    for role_name in ['un-verified', 'verified', 'GCEK-verified']:
        ROLES[role_name] = discord.utils.get(SERVER.roles, name=role_name)

    print(f'{client.user} is connected to {SERVER.name}')

    await integrity_checks(SERVER, client.user, ROLES)
    await notify_un_verified(SERVER, client.user, ROLES['un-verified'])


@client.event
async def on_member_join(member):
    global ROLES
    await member.add_roles(ROLES["un-verified"])
    dm = await member.create_dm()
    customMsg = messageBox['greet and register'] % (member.name,
                                                    client.user,
                                                    SERVER.name)
    await dm.send(customMsg.strip())


@client.event
async def on_member_remove(member):
    global ROLES
    try:
        await member.guild.fetch_ban(member)
        return
    except discord.NotFound:
        await un_register_member(member, ROLES)


@client.event
async def on_message(message):
    global bunker, ROLES
    if message.author == client.user:
        return None
    if(str(message.channel.type) != "private"):
        return None

    content = message.content
    content = re.sub("\t|\n", " ", content)
    content = re.sub("  ", " ", content)
    content.strip()

    id = str(message.author.id)
    for member in SERVER.members:
        if str(member.id) == id:
            bunker[id] = bunker.get(id, DiscordMember(member, ROLES))
            break
    Dmember = bunker[id]
    reply = ""

    if content == '#help':
        reply = messageBox['help']

    elif content == "#register":
        reply = Dmember.register()

    elif content == "#redo":
        reply = Dmember.redo()

    elif content == "#connect":
        reply = await Dmember.connect()

    elif content == "#unregister":
        reply = await Dmember.unregister()

    elif Dmember.registerON:
        reply = Dmember.regInfo(content)
    else:
        reply = messageBox['wrongCommand']

    if not Dmember.registerON:
        del bunker[id]

    await message.channel.send(reply.strip())


if __name__ == "__main__":
    client.run(BOT_TOKEN)