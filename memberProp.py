from settings import SERVER_NAME
import re

class DiscordMember:
    def __init__(self, id):
        self.name = None
        self.id = str(id)
        self.gcekian = None
        self.year = None
        self.branch = None
        self.admn = None
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
        info = re.sub("\t", " ", info)
        info = re.sub("\n", " ", info)
        info = re.sub("  ", " ", info)
        info = info.strip().upper()

        next = self.fetchNext()

        if next == 'name' and len(info) < 40:
            self.name = info.title()

        elif next == 'gcek' and info in ["Y", "YES", "TRUE"]:
            self.gcekian = True

        elif next == 'gcek' and info in ["N", "NO", "FALSE"]:
            self.gcekian = False

        elif next == 'branch' and info in {'CE', 'CS', 'EC', 'EE', 'ME'}:
            self.branch = info

        elif next == 'admission':
            matchObj = re.search("^[0-9]{2}[A-Z][0-9]{3}$",info)
            if matchObj==None:
                return False
            self.admn = matchObj.string

        elif next == 'year':
            if info.startswith("20"):
                info = "2K"+info[2:]

            matchObj = re.search("^2K[0-9]{2}$",info)
            if matchObj == None:
                return False
            self.year = matchObj.string

        else:
            return False

        return True

    def generateMessage(self) -> str:
        next = self.fetchNext()
        if next == "register":
            msg = f"To begin the registration into server {SERVER_NAME} "
            msg += ", issue the command #register "

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
                    Year : {self.year}
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
