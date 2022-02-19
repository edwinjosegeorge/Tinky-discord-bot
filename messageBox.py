messageBox = dict()


messageBox['help'] = """
Type in commands (#) to interact
#help -> displays this message
#register -> Starts the registration process
#unregister -> Removes role and locks channels. You wont't be kicked out.
#connect -> Attempt to verify into server (needs to start registration).
#redo -> Restarts registration process (needs to start registration).

For more help or assistance, contact Server Admins
"""

messageBox['wrongCommand'] = """
Ouch! I did not get you :pleading_face:
""" + messageBox['help']

messageBox['greet and register'] = """
Hello %s , I am %s :sunglasses: from %s :star_struck:
There are a few checks before you can rock and roll the server :student:
Type #register to get started...
Meanwhile...follow us at
  :link: instagram (https://www.instagram.com/tinkerhub.gcek)
  :link: linkedIn (https://in.linkedin.com/company/tinkerhubgcek)
  :link: gitHub (https://github.com/TinkerHub-GCEK)
"""
