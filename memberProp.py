from settings import SERVER_NAME


class DiscordMember:
    def __init__(self, id):
        self.name = None       # string
        self.id = str(id)      # str(discord id)
        self.gcekian = None    # True/False
        self.year = None      # 2K20 2K19 2K18
        self.branch = None     # CS ME CE EE EC
        self.admn = None  # 18B123
        self.registerStart = False

    def fetchNext(self) -> str:
        if self.registerStart is False:
            return "register"

        if self.name is None:
            return "name"

        if self.gcekian is None:
            return "gcek"

        if not self.gcekian:
            return "complete"

        if self.admn is None:
            return "admission"

        if self.year is None:
            return "year"

        if self.branch is None:
            return "branch"

        return "complete"

    def addData(self, info: str) -> bool:
        # add the information to corresponding element, return true on success

        info = info.replace("\t", " ")
        info = info.replace("\n", " ")
        info = info.strip()
        info = info.upper()
        while "  " in info:
            info = info.replace("  ", " ")

        next = self.fetchNext()

        if next == 'name':
            if len(info) > 40:
                return False
            self.name = info.title()
            return True

        elif next == 'gcek':
            if info in ["Y", "YES", "TRUE"]:
                self.gcekian = True
            elif info in ["N", "NO", "FALSE"]:
                self.gcekian = False
            else:
                return False
            return True

        elif next == 'admission':
            accept = len(info) == 6
            accept = accept and info[:2].isnumeric()
            accept = accept and info[2].isalpha()
            accept = accept and info[3:].isnumeric()
            if accept:
                self.admn = info
            return accept

        elif next == 'year':
            accept = len(info) == 4
            accept = accept and info[2:].isnumeric()
            if accept:
                if info.startswith("2K") or info.startswith("20"):
                    self.year = "2K"+info[2:]
                else:
                    accept = False
            return accept

        elif next == 'branch':
            if info in {'CE', 'CS', 'EC', 'EE', 'ME'}:
                self.branch = info
                return True
            return False

        return False

    def generateMessage(self) -> str:
        next = self.fetchNext()
        if next == "register":
            msg = "To begin the registration to server "+SERVER_NAME
            msg += ", issue the command #register"

        elif next == "name":
            msg = "Enter your official name "

        elif next == "gcek":
            msg = "Are you a student at GCE Kannur? [ yes/no ]"

        elif next == "admission":
            msg = "Enter your gcek admission number (eg 16B820)"

        elif next == "year":
            msg = "Enter your batch year [2K21, 2K20, 2K19 ... ]"

        elif next == "branch":
            msg = "Enter your stream [CS, CE, EE, ME, EC]"

        elif next == "complete":
            msg = f"""This is what I received :
                    ID : {self.id}
                    Name : {self.name}
                    GCEK student : {self.gcekian}
                    """
            if self.gcekian:
                msg += f"""Admn No : {self.admn}
                    year : {self.year}
                    Branch : {self.branch}
                    """
            msg += """
            To login the server, type the command #connect
            To re-enter details, type the command #redo"""

        return msg


bunker = dict()  # hold incomplete details


def loadMember(id) -> DiscordMember:
    # Returns an existing or new object for DiscordMember
    bunker[str(id)] = bunker.get(str(id), DiscordMember(str(id)))
    return bunker[str(id)]


def delMember(id) -> None:
    bunker[str(id)] = bunker.get(str(id), DiscordMember(str(id)))
    del bunker[str(id)]
