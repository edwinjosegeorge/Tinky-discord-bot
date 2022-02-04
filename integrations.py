from sqlalchemy import select
from messageBox import messageBox
from PSQL_hooks import Session, CollegeStudent, DB_find, DB_update_id


async def integrity_checks(SERVER, USER, ROLES):

    discord_gcek_verified = dict()
    # fixing roles
    for member in SERVER.members:
        if member.id in {USER.id}:
            continue

        if ROLES['GCEK-verified'] in member.roles:
            id = str(member.id).upper().strip()
            discord_gcek_verified[id] = member
            await member.remove_roles(ROLES["verified"])
            await member.remove_roles(ROLES["un-verified"])

        elif ROLES['verified'] in member.roles:
            await member.remove_roles(ROLES["GCEK-verified"])
            await member.remove_roles(ROLES["un-verified"])

        else:
            await member.add_roles(ROLES['un-verified'])

    with Session() as session:
        # fixing db-discord integrity
        query = select(CollegeStudent).filter(CollegeStudent.id is not None)
        db_reg = session.execute(query).all()
        for row in db_reg:
            record = row[0]
            memID = record.id
            if memID not in discord_gcek_verified:
                record.id = None
                continue
            del discord_gcek_verified[memID]
        session.commit()

        for memID in discord_gcek_verified:
            member = discord_gcek_verified[memID]
            await member.remove_roles(ROLES['GCEK-verified'])
            await member.add_roles(ROLES['verified'])


async def notify_un_verified(SERVER, USER, ROLE):
    # send message to all unverified
    for member in SERVER.members:
        if member.id in {USER.id}:
            continue
        if ROLE not in member.roles:
            continue

        dm = await member.create_dm()
        customMsg = messageBox['greet and register'] % (
            member.name, USER.name, SERVER.name)
        await dm.send(customMsg.strip())


async def register_member(Dmember) -> str:
    """
    registers the member by checking rules
    """
    ROLES = Dmember.serverRoles
    member = Dmember.memberObj
    new_id = str(member.id)

    if ROLES['verified'] in member.roles:
        return "pre-verified"
    if ROLES['GCEK-verified'] in member.roles:
        return "pre-verified"

    DB_pre_records = DB_find(id=new_id)
    if len(DB_pre_records) != 0:
        return "multiple id"

    if not Dmember.gcekian:
        await member.remove_roles(ROLES['un-verified'])
        await member.add_roles(ROLES['verified'])
        await member.edit(nick=(Dmember.name+" 🎓"))
        return 'success'

    # ADD member id in DB
    DB_pre_records = DB_find(admn=Dmember.admn)
    if len(DB_pre_records) == 0:
        return "admn not found"
    if DB_pre_records[0].id is not None:
        return "admn pre-occupied"
    if not Dmember.nameSimilarity(DB_pre_records[0].name):
        return "wrong details"
    if Dmember.branch != DB_pre_records[0].branch:
        return "wrong details"
    if Dmember.year != DB_pre_records[0].year:
        return "wrong details"
    if not DB_update_id(admn=Dmember.admn, id=Dmember.id):
        return "update error"

    # update gcekian member roles:
    await member.remove_roles(ROLES['un-verified'])
    await member.add_roles(ROLES['GCEK-verified'])
    new_name = (DB_pre_records[0].name).title()
    await member.edit(nick=(new_name+" 🎓"))
    return "success"


async def un_register_member(member, ROLES) -> bool:
    """
    remove member id from DB
    return True on success
    """
    try:
        records = DB_find(id=str(member.id))
        for clgStuObj in records:
            DB_update_id(admn=clgStuObj.admn, id=None)

        # update member roles:
        await member.add_roles(ROLES['un-verified'])
        await member.remove_roles(ROLES['verified'])
        await member.remove_roles(ROLES['GCEK-verified'])
        await member.edit(nick=f"{member.name}#{member.discriminator}")
        return True
    except Exception as e:
        print(e)
        return False
