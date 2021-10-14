import os
import discord
import difflib
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SERVER_ID = os.getenv("SERVER_ID")
SERVER_NAME = "server"
intents = discord.Intents.all()
bunker = dict()  # hold incomplete details


def memberInstance(id):
    # Returns an existing or new object for DiscordMember
    bunker[str(id)] = bunker.get(str(id), DiscordMember(str(id)))
    return bunker[str(id)]


def database_add(Dmember):
    # add new record or update existing record in Discord Register list
    if not Dmember.valid():
        return False

    data = pd.read_excel('discordList.xlsx')
    if len(data[data['ID'].str.upper() == str(Dmember.id)]) == 1:
        # data already present
        # TODO: Update routine
        return True

    gcekinfo = ""
    if not Dmember.GCEKian:
        gcekinfo = "False"
    else:
        gcekinfo = f"{Dmember.branch} {Dmember.batch}"

    newData = {'ID': Dmember.id, 'Dname': Dmember.name, 'Class': gcekinfo}
    data = data.append(newData, ignore_index=True)
    data.to_excel('discordList.xlsx', index=False)
    return True


def database_search_register(memberID):
    # searches the Discord Register for id, if found return the row, else FALSE
    pass


def database_is_GCEKian(Dmember):
    # Checks if the member is a GCEKian or not. Look and maps GCEK list
    # if match found, update name and return True, else False

    data = pd.read_excel('GCEKList.xlsx', sheet_name=Dmember.branch)
    data = data[data['admission'].str.upper() == Dmember.admission.upper()]

    # map branch and year
    search = f"{Dmember.branch} {Dmember.batch}".upper()
    if Dmember.branch == "EC":
        data = data[(data['Class'].str.upper() == (search+"A"))
                    | (data['Class'].str.upper() == (search+"B"))]
    else:
        data = data[data['Class'].str.upper() == search]

    data = data[data['Class'].str.upper() == search.upper()]

    if len(data) != 1:
        return False

    # compare name
    seq = difflib.SequenceMatcher(None, data['Name'].str.upper().item(),
                                  Dmember.name.upper())
    similar = float(seq.ratio()) > 0.8
    if similar:
        Dmember.name = str(data['Name'].str.upper().item()).title()
    return similar


def database_remove(memberID):
    pass


class DiscordMember:
    def __init__(self, id):
        self.name = None  # string
        self.id = id  # number
        self.GCEKian = None  # True/False
        self.batch = None  # 2K20 2K19 2K18
        self.branch = None  # CS ME CE EE EC
        self.admission = None  # 18B123
        self.registerStart = False

    def fetchNext(self):
        if self.id is None:
            return "discord id"

        if self.registerStart is False:
            return "register"

        if self.name is None:
            return "name"

        if self.GCEKian is None:
            return "GCEK"

        if not self.GCEKian:
            return "complete"

        if self.admission is None:
            return "admission"

        if self.batch is None:
            return "batch"

        if self.branch is None:
            return "branch"
        return "complete"

    def valid(self):
        if self.fetchNext() != "complete":
            return False
        if self.GCEKian:
            return database_is_GCEKian(self)
        return True

    async def plugin(self):
        guild = discord.utils.get(client.guilds, id=SERVER_ID)
        for member in guild.members:
            if member.id == self.id:
                await member.edit(nick=(self.name+" 🎓"))

                role = discord.utils.get(guild.roles, name="un-verified")
                await member.remove_roles(role)
                if self.GCEKian:
                    role = discord.utils.get(guild.roles, name="GCEK-verified")
                else:
                    role = discord.utils.get(guild.roles, name="verified")
                await member.add_roles(role)
                return True
        return False

    async def unplug(self):
        guild = discord.utils.get(client.guilds, id=SERVER_ID)
        for member in guild.members:
            if member.id == self.id:
                await member.edit(nick=(self.name))

                role = discord.utils.get(guild.roles, name="un-verified")
                await member.add_roles(role)
                if self.GCEKian:
                    role = discord.utils.get(guild.roles, name="GCEK-verified")
                else:
                    role = discord.utils.get(guild.roles, name="verified")
                await member.remove_roles(role)
                return None

    def generateMessage(self):
        next = self.fetchNext()
        if next == "register":
            msg = f"To begin the registration to server {SERVER_NAME}, issue the command #register"

        elif next == "name":
            msg = """Enter your official name using the command #name
                eg      #name This is my Name"""

        elif next == "GCEK":
            msg = """Are you a student at GCE Kannur?
        respond 'yes' by issuing  the command   #GCEK yes
        respond 'no' by issuing  the command   #GCEK no"""

        elif next == "admission":
            msg = "Enter your GCEK admission number using the command #ADMN xxxxxx"

        elif next == "batch":
            msg = "Enter your batch year [2K21, 2K20, 2K19 ... ] using the command #batch 2Kxx"

        elif next == "branch":
            msg = "Enter your stream [CS, CE, EE, ME, EC] using the command #branch XX"

        elif next == "complete":
            msg = f"""This is what I received :
                    ID : {self.id}
                    Name : {self.name}
                    GCEK student : {self.GCEKian}
                    """
            if self.GCEKian:
                msg += f"""AddNo : {self.admission}
                    Batch : {self.batch}
                    Branch : {self.branch}
                    """
            msg += """
            To login the server, type the command #connect
            To re-enter details, type the command #redo"""

        return msg


class MyClient(discord.Client):
    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)

    async def on_ready(self):
        global SERVER_NAME

        print(f'Logged on as {self.user}')
        guild = discord.utils.get(client.guilds, id=SERVER_ID)

        print(f'{self.user} is connected to {guild.name}(id: {guild.id})\n')
        SERVER_NAME = guild.name

        role = discord.utils.get(guild.roles, name="un-verified")
        for member in guild.members:
            if member.id in {self.user.id}:
                continue
            if role not in member.roles:
                continue

            dm = await member.create_dm()
            await dm.send(f"""Hello {member.name}! Welcome to {SERVER_NAME}
        Lets plug you into the server...!
        Use the command #register to begin the setup!
        """)

    async def on_message(self, message):
        if message.author == self.user:
            return None

        if(str(message.channel.type) != "private"):
            return None

        thisMember = memberInstance(message.author.id)

        if str(message.content).strip() == "#register":
            if not(self.has_role('un-verified', message.author.id)):
                await message.channel.send(f"It seems you have already joined {SERVER_NAME}")
                del bunker[str(message.author.id)]
                return None

            elif thisMember.registerStart:
                await message.channel.send("Complete the current registration process")
            else:
                thisMember.registerStart = True
                await message.channel.send(f"Lets plug you into the server: {SERVER_NAME}")

        elif str(message.content).startswith("#name "):
            if thisMember.fetchNext() == "name":
                thisMember.name = str(message.content)[6:].strip().title()
        elif str(message.content).startswith("#GCEK "):
            if thisMember.fetchNext() == "GCEK":
                if str(message.content)[6:].strip().lower() == "yes":
                    thisMember.GCEKian = True
                elif str(message.content)[6:].strip().lower() == "no":
                    thisMember.GCEKian = False
        elif str(message.content).startswith("#ADMN "):
            if thisMember.fetchNext() == "admission":
                thisMember.admission = str(message.content)[6:].strip().upper()
        elif str(message.content).startswith("#batch 2"):
            if thisMember.fetchNext() == "batch":
                year = str(message.content)[7:].strip().upper()
                if year[2:].isnumeric():
                    thisMember.batch = year
        elif str(message.content).startswith("#branch "):
            if thisMember.fetchNext() == "branch":
                branch = str(message.content)[7:].strip().upper()
                if branch in ['CS', 'ME', 'EE', 'EC', 'CE']:
                    thisMember.branch = branch
        elif str(message.content) == "#redo":
            if thisMember.fetchNext() == "complete":
                del bunker[str(message.author.id)]
                thisMember = memberInstance(message.author.id)
        elif str(message.content) == "#connect":
            if thisMember.fetchNext() == "complete":
                try:
                    if thisMember.valid() and (await thisMember.plugin()) and database_add(thisMember):
                        await message.channel.send(f"Lets rock and roll the server! See you at {SERVER_NAME}")
                    else:
                        await thisMember.unplug()
                        database_remove(thisMember.id)
                        await message.channel.send("Ops! something went wrong... have you entered correct details? lets try once more... issue the command #register to get started")
                except Exception as e:
                    print(e)
                finally:
                    del bunker[str(message.author.id)]
                    return None
        elif str(message.content).startswith("#"):
            await message.channel.send("I am sorry, I did not quite understand you. Have you entered the command correctly?")
        else:
            print(message.author, ":", message.content)
            return None

        await message.channel.send(thisMember.generateMessage())
        print(message.author, ":", message.content)

    async def on_member_join(self, member):
        guild = discord.utils.get(self.guilds, id=SERVER_ID)
        role = discord.utils.get(guild.roles, name="un-verified")
        await member.add_roles(role)

        dm = await member.create_dm()
        await dm.send(f"""Hello {member.name}! Welcome to {SERVER_NAME}
    Lets plug you into the server...!
    Use the command #register to begin the setup!
    """)

    async def on_member_remove(self, member):
        database_remove(member.id)
        if self.has_role("un-verified", member.id):
            return None

        dm = await member.create_dm()
        await dm.send(f"Sorry to see you leave {SERVER_NAME}")

    def has_role(self, role_name, member_id):
        guild = discord.utils.get(self.guilds, id=SERVER_ID)
        for member in guild.members:
            if member.id == member.id:
                for role in member.roles:
                    if role.name == role_name:
                        return True
                return False
        return False


client = MyClient(intents=intents)
client.run(BOT_TOKEN)
