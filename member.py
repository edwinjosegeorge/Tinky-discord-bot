import re
from messageBox import messageBox
from difflib import SequenceMatcher
from integrations import register_member, un_register_member


class DiscordMember:
    """
    Class that holds attributes of a discord member
    """

    def __init__(self, memObj, ROLES):
        self.memberObj = memObj
        self.id = str(memObj.id).upper()
        self.serverRoles = ROLES
        self.registerON = False

        self.name = None
        self.gcekian = None
        self.admn = None
        self.year = None
        self.branch = None

    def register(self) -> str:
        if self.registerON:
            return "Complete the current registration"

        # check if already registered
        if self.serverRoles["verified"] in self.memberObj.roles:
            return "You are already in the server!"
        if self.serverRoles["GCEK-verified"] in self.memberObj.roles:
            return "You are already in the server!"

        self.registerON = True
        return "Enter your official name"

    def redo(self) -> str:
        if not self.registerON:
            return "Type #register to get started"
        self.name = None
        self.gcekian = None
        self.admn = None
        self.year = None
        self.branch = None
        return "Enter your official name"

    async def connect(self) -> str:
        if not self.registerON:
            return "Type #register to get started"
        if self.gcekian is None:
            return "Complete the current registration"
        if self.gcekian and self.branch is None:
            return "Complete the current registration"

        self.registerON = False

        status = await register_member(Dmember=self)

        if status == "success":
            return messageBox['registrationSuccess']
        if status == "multiple id":
            return "It seems you are already logged in the server with some other name. Try #unregister to reset roles."
        if status == "pre-verified":
            return "You are already verified in the server! Try #unregister to reset roles."
        if status == "admn not found":
            return f"Ops!... Cannot find the admn no: {self.admn}"
        if status == "admn pre-occupied":
            return f"Ops!... Admn no: {self.admn} is pre-occupied"
        if status == "wrong details":
            return "Ops!... Entries do not match!"
        return "Ops!... something went wrong!"

    async def unregister(self):
        status = await un_register_member(member=self.memberObj, ROLES=self.serverRoles)
        self.registerON = False
        if status:
            return messageBox['unregistrationSuccess']
        return "Ops!... something went wrong!"

    def regInfo(self, info: str) -> str:
        if not self.registerON:
            return "Type #register to get started"

        if self.name is None:
            self.name = info.upper()
            return "Are you a student at GCE Kannur? [ yes/no ]"

        if self.gcekian is None:
            info = info.upper()
            if info in ["Y", "YES", "TRUE"]:
                self.gcekian = True
                return "Enter your gcek admission number (eg 16B820)"

            elif info in ["N", "NO", "FALSE"]:
                self.gcekian = False
                msg = "This is what I received : \n"
                msg += f"\t ID : {self.id} \n"
                msg += f"\t Name : {self.name} \n"
                msg += f"\t GCEK student : {self.gcekian} \n"
                msg += "\nTo login the server, type the command #connect \n"
                msg += "To re-enter details, type the command #redo"
                return msg

            msg = "Ops! I did not understand...\n"
            msg += "Are you a student at GCE Kannur? [ yes/no ]"
            return msg

        if self.gcekian and self.admn is None:
            info = info.upper()
            matchObj = re.search("^[0-9]{2}[A-Z][0-9]{3}$", info)
            if matchObj is None:
                msg = "Ops! I did not understand...\n"
                msg += "Enter your gcek admission number (eg 16B820)"
                return msg

            self.admn = matchObj.string
            return "Enter your batch year [2K21, 2K20, 2K19 ... ]"

        if not self.gcekian:
            msg = "Ops! I did not understand... its time to plug you in...\n"
            msg += "This is what I received : \n"
            msg += f"\t ID : {self.id} \n"
            msg += f"\t Name : {self.name} \n"
            msg += f"\t GCEK student : {self.gcekian} \n"
            msg += "\nTo login the server, type the command #connect \n"
            msg += "To re-enter details, type the command #redo"
            return msg

        if self.year is None:
            info = info.upper()
            if info.startswith("20"):
                info = "2K"+info[2:]
            matchObj = re.search("^2K[0-9]{2}$", info)

            if matchObj is None:
                msg = "Ops! I did not understand...\n"
                msg += "Enter your batch year [2K21, 2K20, 2K19 ... ]"
                return msg

            self.year = matchObj.string
            return "Enter your stream [CS, CE, EE, ME, EC]"

        if self.branch is None:
            info = info.upper()
            if info not in {'CE', 'CS', 'EC', 'EE', 'ME'}:
                msg = "Ops! I did not understand...\n"
                msg += "Enter your stream [CS, CE, EE, ME, EC]"
                return msg
            self.branch = info
            msg = "This is what I received : \n"
            msg += f"\t ID : {self.id} \n"
            msg += f"\t Name : {self.name} \n"
            msg += f"\t GCEK student : {self.gcekian} \n"
            msg += f"\t Admn No : {self.admn}\n"
            msg += f"\t Year : {self.year}\n"
            msg += f"\t Branch : {self.branch}\n"
            msg += "\nTo login the server, type the command #connect \n"
            msg += "To re-enter details, type the command #redo"
            return msg

        msg = "Ops! I did not understand... its time to plug you in...\n"
        msg += "This is what I received : \n"
        msg += f"\t ID : {self.id} \n"
        msg += f"\t Name : {self.name} \n"
        msg += f"\t GCEK student : {self.gcekian} \n"
        msg += f"\t Admn No : {self.admn}\n"
        msg += f"\t Year : {self.year}\n"
        msg += f"\t Branch : {self.branch}\n"
        msg += "\nTo login the server, type the command #connect \n"
        msg += "To re-enter details, type the command #redo"
        return msg

    def nameSimilarity(self, newName):
        r = float(SequenceMatcher(None, self.name, newName).ratio())
        return r > 0.8
