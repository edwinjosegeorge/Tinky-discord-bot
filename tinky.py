import discord
from memberProp import loadMember, delMember
from psqlHandler import DataBunker
from settings import SERVER_NAME, BOT_TOKEN, SERVER_ID

intents = discord.Intents.all()


class MyClient(discord.Client):
    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)

    async def on_ready(self):
        global SERVER_NAME, SERVER_ID

        print(f'Logged on as {self.user}')
        guild = discord.utils.get(client.guilds, id=SERVER_ID)

        print(f'{self.user} is connected to {guild.name}(id: {guild.id})')

        # send message to unverified
        role = discord.utils.get(guild.roles, name="un-verified")
        for member in guild.members:
            if member.id in {self.user.id}:
                continue
            if role not in member.roles:
                continue

            dm = await member.create_dm()
            await dm.send(f"""Hello {member.name}! Welcome to {SERVER_NAME}
        Follow us at
        + instagram https://www.instagram.com/tinkerhub.gcek/
        + linkedIn https://in.linkedin.com/company/tinkerhubgcek

        Meanwhile...Lets plug you into the discord server...!
        Use the command  #register to begin the setup!
        """)

    async def on_message(self, message):
        if message.author == self.user:
            return None

        if(str(message.channel.type) != "private"):
            return None

        thisMember = loadMember(message.author.id)
        # print(message.author, ":", message.content)

        content = str(message.content).strip()
        reply = ""
        if content == "#register":
            if not(self.has_role('un-verified', message.author.id)):
                reply = f"""It seems you have already joined {SERVER_NAME}
                Hmm... have you checked us on
                + instagram https://www.instagram.com/tinkerhub.gcek/
                + linkedIn https://in.linkedin.com/company/tinkerhubgcek"""
                delMember(message.author.id)

            elif thisMember.registerStart:
                reply = "Complete the current registration process"

            else:
                thisMember.registerStart = True
                reply = f"""Lets plug you into the server {SERVER_NAME}
                {thisMember.generateMessage()}"""

        elif content == "#redo":
            if thisMember.fetchNext() == "complete":
                delMember(message.author.id)
                thisMember = loadMember(message.author.id)
                thisMember.registerStart = True
            reply = thisMember.generateMessage()

        elif content == "#connect":
            if thisMember.fetchNext() == "complete":
                db = DataBunker()

                oldRecord = False
                if thisMember.gcekian:
                    oldRecord = db.search(
                        "discord_list", {'gcekian': thisMember.admn})

                oldRecord = oldRecord or db.search(
                        "discord_list", {'id': thisMember.id})

                if oldRecord:
                    reply = "Ops! It seems you have already joined the server "
                    reply += f"{SERVER_NAME}. Contact admins for more info..."

                elif not(thisMember.gcekian) or db.check_gcekian(thisMember):
                    dbinfo = dict()
                    dbinfo['name'] = thisMember.name.upper()
                    dbinfo['id'] = thisMember.id
                    dbinfo['gcekian'] = "FALSE"
                    if thisMember.gcekian:
                        dbinfo['gcekian'] = thisMember.admn

                    if db.add('discord_list', dbinfo):
                        try:
                            await self.plugin(thisMember)
                            reply = f"""Lets rock and roll the server.
                        See you at {SERVER_NAME}
                        Meanwhile...follow us at
                        + instagram https://www.instagram.com/tinkerhub.gcek/
                        + linkedIn https://in.linkedin.com/company/tinkerhubgcek """
                        except Exception as e:
                            print(e)
                            db.remove("discord_list", {'id': thisMember.id})
                            reply = "Ops! something went wrong... "
                            reply += "try again after after a while. "
                            reply += "Issue the command #register to try again"
                    else:
                        reply = "Ops! something went wrong... "
                        reply += "try again after after a while. "
                        reply += "Issue the command #register to try again"
                else:
                    reply = "Ops! Cannot find you in the GCEK list. "
                    reply += "Have you entered name and admn correctly? "
                    reply += "Issue the command #register to try again"
                delMember(message.author.id)
            else:
                reply = thisMember.generateMessage()
        elif content.startswith("#"):
            reply = "I did not quite understand you. "
            reply += f"""Have you entered the command correctly?
            {thisMember.generateMessage()}"""

        elif thisMember.registerStart:
            thisMember.addData(content)
            reply = thisMember.generateMessage()
        else:
            delMember(message.author.id)
            return None
        await message.channel.send(reply)

    async def on_member_join(self, member):
        # trigger when someone new joins!

        guild = discord.utils.get(self.guilds, id=SERVER_ID)
        role = discord.utils.get(guild.roles, name="un-verified")
        await member.add_roles(role)

        dm = await member.create_dm()
        await dm.send(f"""Hello {member.name}! Welcome to {SERVER_NAME}
    Lets plug you into the server...!
    Use the command #register to begin the setup!
    """)

    async def on_member_remove(self, member):
        db = DataBunker()
        db.remove("discord_list", {'id': str(member.id)})

    def has_role(self, role_name, member_id):
        guild = discord.utils.get(self.guilds, id=SERVER_ID)
        for member in guild.members:
            if member.id == int(member_id):
                for role in member.roles:
                    if role.name == role_name:
                        return True
                return False
        return False

    async def plugin(self, Dmember):
        guild = discord.utils.get(self.guilds, id=SERVER_ID)
        for member in guild.members:
            if str(member.id) == Dmember.id:
                await member.edit(nick=(Dmember.name+" 🎓"))

                role = discord.utils.get(guild.roles, name="un-verified")
                await member.remove_roles(role)
                if Dmember.gcekian:
                    role = discord.utils.get(guild.roles, name="GCEK-verified")
                else:
                    role = discord.utils.get(guild.roles, name="verified")
                await member.add_roles(role)
                return True
        return False

    async def unplug(self, Dmember):
        guild = discord.utils.get(client.guilds, id=SERVER_ID)
        for member in guild.members:
            if str(member.id) == str(Dmember.id):
                await member.edit(nick=f"{member.name}#{member.discriminator}")

                role = discord.utils.get(guild.roles, name="un-verified")
                await member.add_roles(role)

                role = discord.utils.get(guild.roles, name="verified")
                if self.GCEKian:
                    role = discord.utils.get(guild.roles, name="GCEK-verified")
                await member.remove_roles(role)
                return None


client = MyClient(intents=intents)
if __name__ == "__main__":
    client.run(BOT_TOKEN)
    client.run(BOT_TOKEN)
