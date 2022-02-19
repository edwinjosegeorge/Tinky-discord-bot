from database.tables import CollegeStudent
from database.hooks import DB_find, DB_update


async def push_msg_for_role(MEMBER, ROLE, MSG: str) -> None:
    """
    Push direct message to a member with specific role
    """
    if ROLE in MEMBER.roles:
        dm = await MEMBER.create_dm()
        await dm.send(MSG.strip())


async def register_member(Dmember) -> str:
    """
    registers the member by checking rules
    returns various status
    """
    try:
        ROLES = Dmember.serverRoles
        member = Dmember.memberObj
        new_id = str(member.id)

        if ROLES['verified'] in member.roles:
            return "pre-verified"
        if ROLES['GCEK-verified'] in member.roles:
            return "pre-verified"

        DB_record = DB_find(CollegeStudent, id=new_id)
        if len(DB_record) != 0:
            return "multiple id"

        if not Dmember.gcekian:
            await member.remove_roles(ROLES['un-verified'])
            await member.add_roles(ROLES['verified'])
            await member.edit(nick=Dmember.nickname())
            return 'registrationSuccess'

        # ADD member id in DB
        DB_record = DB_find(CollegeStudent, admn=Dmember.admn)
        if len(DB_record) == 0:
            return "admn not found"
        if DB_record[0].id is not None:
            return "admn pre-occupied"
        if not DB_record[0].nameSimilarity(Dmember.name.upper()):
            return "wrong details"
        if Dmember.branch != DB_record[0].branch:
            return "wrong details"
        if Dmember.year != DB_record[0].year:
            return "wrong details"
        if not DB_update(CollegeStudent, {'admn': Dmember.admn}, {'id': new_id}):
            return "error"

        # update gcekian member roles:
        await member.remove_roles(ROLES['un-verified'])
        await member.add_roles(ROLES['GCEK-verified'])
        await member.edit(nick=Dmember.nickname())
        return "registrationSuccess"
    except Exception as e:
        print("Exception at member.support.register_member ", e)
        return 'error'


async def un_register_member(member, ROLES) -> bool:
    """
    remove member id from DB
    return True on success
    """
    try:
        records = DB_find(CollegeStudent, id=str(member.id))
        for clgStuObj in records:
            DB_update(CollegeStudent, {'admn': clgStuObj.admn}, {'id': ""})

        # update member roles:
        await member.add_roles(ROLES['un-verified'])
        await member.remove_roles(ROLES['verified'])
        await member.remove_roles(ROLES['GCEK-verified'])
        await member.edit(nick=f"{member.name}#{member.discriminator}")
        return True
    except Exception as e:
        print("Exception at member.support.un_register_member ", e)
        return False
