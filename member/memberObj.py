import re
from messageBox import messageBox
from member.support import register_member, un_register_member


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

    def nickname(self) -> str:
        if self.name is not None:
            return self.name.title()+" 🎓"
        return self.memberObj.display_name

    def register(self) -> str:
        if self.registerON:
            return messageBox['registationActive']

        # check if already registered
        if self.serverRoles["verified"] in self.memberObj.roles:
            return messageBox['pre-verified']
        if self.serverRoles["GCEK-verified"] in self.memberObj.roles:
            return messageBox['pre-verified']

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
            return messageBox['registationActive']
        if self.gcekian and self.branch is None:
            return messageBox['registationActive']

        self.registerON = False
        status = await register_member(Dmember=self)
        if status in messageBox:
            return messageBox[status]
        return messageBox['error']

    async def unregister(self):
        status = await un_register_member(member=self.memberObj,
                                          ROLES=self.serverRoles)
        self.registerON = False
        if status:
            return messageBox['unregistrationSuccess']
        return messageBox['error']

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
                msg = messageBox['confirmInfo'] % (self.id, self.name,
                                                   self.gcekian)
                return msg

            msg = "Ops! I did not understand...\n"
            msg += "Are you a student at GCE Kannur? [ yes/no ]"
            return msg

        if not self.gcekian:
            msg = "Ops! I did not understand... its time to plug you in...\n"
            msg += messageBox['confirmInfo'] % (self.id, self.name,
                                                self.gcekian)
            return msg

        if self.admn is None:
            info = info.upper()
            matchObj = re.search("^[0-9]{2}[A-Z][0-9]{3}$", info)
            if matchObj is None:
                msg = "Ops! I did not understand...\n"
                msg += "Enter your gcek admission number (eg 16B820)"
                return msg

            self.admn = matchObj.string
            return "Enter your batch year [2K21, 2K20, 2K19 ... ]"

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
            msg = messageBox['GCEK-confirmatInfo'] % (self.id, self.name,
                                                      self.gcekian, self.admn,
                                                      self.year, self.branch)
            return msg

        msg = "Ops! I did not understand... its time to plug you in...\n"
        msg += messageBox['GCEK-confirmatInfo'] % (self.id, self.name,
                                                   self.gcekian, self.admn,
                                                   self.year, self.branch)
        return msg
        return msg
        return msg
        return msg
