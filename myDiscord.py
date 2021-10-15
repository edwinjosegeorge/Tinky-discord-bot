import os
import discord
import difflib
import psycopg2
import urllib.parse as urlparse
from dotenv import load_dotenv


load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SERVER_ID = int(os.getenv("SERVER_ID"))
SERVER_NAME = "server"
intents = discord.Intents.all()
bunker = dict()  # hold incomplete details


def memberInstance(id):
    # Returns an existing or new object for DiscordMember
    bunker[str(id)] = bunker.get(str(id), DiscordMember(str(id)))
    return bunker[str(id)]


def database_search_register(key, value):
    # searches the Discord Register for key, if found return True, else False
    con = None
    status = False
    try:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        con = psycopg2.connect(dbname=dbname, user=user,
                               password=password, host=host, port=port)
        cursor = con.cursor()

        query = f"SELECT id FROM discord_list WHERE {key}='{str(value)}'"
        cursor.execute(query)
        status = cursor.rowcount > 0
        cursor.close()
    except Exception as error:
        print('discord_list search:error :: {}'.format(error))
    finally:
        if con is not None:
            con.close()
            print('discord_list search status', status)
            return status


def database_add(Dmember):
    # add new record or update existing record in Discord Register list
    con = None
    status = False
    try:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        con = psycopg2.connect(dbname=dbname, user=user,
                               password=password, host=host, port=port)
        cursor = con.cursor()

        # Add new entry
        id = str(Dmember.id)
        name = Dmember.name.title()
        if Dmember.GCEKian:
            gcekian = str(Dmember.admission)
        else:
            gcekian = "False"

        if database_search_register("id", Dmember.id):
            query = f"UPDATE discord_list \
            SET name='{name}', gcekian='{gcekian}'\
            WHERE id='{id}'"
        else:
            query = f"INSERT INTO discord_list (id, name, gcekian) \
        VALUES ('{id}', '{name}', '{gcekian}')"

        cursor.execute(query)
        con.commit()
        cursor.close()
        status = True
    except Exception as error:
        print('discord_list insert:error :: {}'.format(error))
    finally:
        if con is not None:
            con.close()
            print('discord_list insert status', status)
            return status


def database_is_GCEKian(Dmember):
    # Checks if the member is a GCEKian or not. Look and maps GCEK list
    # if match found, update name and return True, else False

    con = None
    status = False
    try:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        con = psycopg2.connect(dbname=dbname, user=user,
                               password=password, host=host, port=port)
        cursor = con.cursor()

        query = f"SELECT name,branch,year FROM gcek_list \
        WHERE admn='{str(Dmember.admission).upper()}'"
        cursor.execute(query)

        record = cursor.fetchone()
        if len(record) != 0:
            status = True
        if status and str(record[1]).upper().strip() == Dmember.branch.strip().upper():
            if str(record[2]).upper().strip() == Dmember.batch.strip().upper():
                # compare name
                seq = difflib.SequenceMatcher(None, str(record[0]).strip().upper(),
                                              Dmember.name.strip().upper())
                status = float(seq.ratio()) > 0.8
                if status:
                    Dmember.name = str(record[0]).strip().title()
            else:
                status = False
        else:
            status = False
        cursor.close()
    except Exception as error:
        print('gcek_list search:error :: {}'.format(error))
    finally:
        if con is not None:
            con.close()
            print(f'gcek_list search status', status)
            return status


def database_remove(memberID):
    con = None
    status = False
    try:
        url = urlparse.urlparse(os.environ['DATABASE_URL'])
        dbname = url.path[1:]
        user = url.username
        password = url.password
        host = url.hostname
        port = url.port
        con = psycopg2.connect(dbname=dbname, user=user,
                               password=password, host=host, port=port)
        cursor = con.cursor()

        # Add new entry
        id = str(memberID)
        query = f"DELETE FROM discord_list WHERE id='{id}'"

        cursor.execute(query)
        con.commit()
        cursor.close()
        status = True
    except Exception as error:
        print('discord_list remove:error :: {}'.format(error))
    finally:
        if con is not None:
            con.close()
            print('discord_list remove status', status)
            return status


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
            if str(member.id) == str(self.id):
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
                eg      #name 'This is my Name'"""

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
        print(message.author, ":", message.content)

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
                    if database_search_register("id", str(thisMember.id)) or database_search_register("gcekian", str(thisMember.admission).upper()):
                        await message.channel.send(f"Ops! It seems you have already been in {SERVER_NAME}. Try contacting the server admins for more info...")
                    elif thisMember.valid() and database_add(thisMember):
                        print("plugging in...")
                        if (await thisMember.plugin()):
                            await message.channel.send(f"Lets rock and roll the server! See you at {SERVER_NAME}")
                        else:
                            await thisMember.unplug()
                            database_remove(thisMember.id)
                    else:
                        await thisMember.unplug()
                        database_remove(thisMember.id)
                        await message.channel.send("Ops! something went wrong... have you entered correct details? lets try once more... issue the command #register to get started")
                except Exception as e:
                    print("something went wrong! ", e)
                finally:
                    del bunker[str(message.author.id)]
                    return None
        elif str(message.content).startswith("#"):
            await message.channel.send("I am sorry, I did not quite understand you. Have you entered the command correctly?")
        else:
            print(message.author, ":", message.content)
            return None

        await message.channel.send(thisMember.generateMessage())

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

    def has_role(self, role_name, member_id):
        guild = discord.utils.get(self.guilds, id=SERVER_ID)
        for member in guild.members:
            if member.id == int(member_id):
                for role in member.roles:
                    if role.name == role_name:
                        return True
                return False
        return False


client = MyClient(intents=intents)
if __name__ == "__main__":
    client.run(BOT_TOKEN)
