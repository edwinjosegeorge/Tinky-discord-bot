import re
import discord
from messageBox import messageBox
from settings import BOT_TOKEN, SERVER_ID

from member.memberObj import DiscordMember

from database.tables import initialize as DB_init
from database.support import integrity_checks

from asyncio import ensure_future as fire_and_forget
from instagram import push_notification_loop as IG_loop


intents = discord.Intents.all()
client = discord.Client(intents=intents)
SERVER = None
ROLES = dict()  # cache the role objects
bunker = dict()  # cache discord incomplete details


@client.event
async def on_ready():
    global SERVER, ROLES
    DB_init()
    SERVER = discord.utils.get(client.guilds, id=SERVER_ID)
    print(f'{client.user} is connected to {SERVER.name}')
    for role_name in ['un-verified', 'verified', 'GCEK-verified']:
        ROLES[role_name] = discord.utils.get(SERVER.roles, name=role_name)

    # it is a lo0oong operation. execute only if restarting after a long time
    '''
    await integrity_checks(SERVER, client.user, ROLES)

    print("Notifying un-verified members")
    for member in SERVER.members:
        if member.id in {client.user.id}:
            continue
        if ROLES['un-verified'] not in member.roles:
            continue
        try:
            dm = await member.create_dm()
            msg = messageBox['greet and register'] % (member.name,
                                                      client.user.name,
                                                      SERVER.name)
            await dm.send(msg.strip())
        except Exception as e:
            print(f"Exception while notifying {member.display_name} : ", e)
    '''
    # dispatching new task
    fire_and_forget(IG_loop(client, 3600))


@client.event
async def on_member_join(member):
    global ROLES
    await member.add_roles(ROLES["un-verified"])
    dm = await member.create_dm()
    customMsg = messageBox['greet and register'] % (member.name,
                                                    client.user.name,
                                                    SERVER.name)
    print("customMsg")
    await dm.send(customMsg.strip())


@client.event
async def on_member_remove(member):
    global ROLES
    try:
        await member.guild.fetch_ban(member)
        return
    except discord.NotFound:
        Dmember = DiscordMember(member, ROLES)
        await Dmember.unregister()


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
    if id not in bunker:
        for member in SERVER.members:
            if str(member.id) == id:
                bunker[id] = DiscordMember(member, ROLES)
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
