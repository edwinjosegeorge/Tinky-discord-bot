from messageBox import messageBox
from database.tables import CollegeStudent
from database.hooks import DB_find, DB_update


async def integrity_checks(SERVER, USER, ROLES: dict) -> None:
    """
    Resolves Server and DB integrity. Ensures the roles are corretly matched
    """
    print("DB integrity checks started...")

    gcek_verified = dict()

    # fetch DB records
    for obj in DB_find(CollegeStudent):
        if obj.id == "":
            continue
        gcek_verified[obj.id] = obj

    for member in SERVER.members:
        if member.id in {USER.id}:
            continue
        try:
            id = str(member.id).strip().upper()
            nickname = member.display_name
            if ROLES['GCEK-verified'] in member.roles and id in gcek_verified:
                if nickname != gcek_verified[id].nickname:
                    await member.edit(nick=gcek_verified[id].nickname)
                await member.remove_roles(ROLES["verified"])
                await member.remove_roles(ROLES["un-verified"])
                del gcek_verified[id]

            elif ROLES['verified'] in member.roles:
                if "🎓" not in nickname:
                    await member.edit(nick=nickname.strip()+" 🎓")
                await member.remove_roles(ROLES["GCEK-verified"])
                await member.remove_roles(ROLES["un-verified"])

            else:
                await member.remove_roles(ROLES["GCEK-verified"])
                await member.remove_roles(ROLES["verified"])
                await member.add_roles(ROLES['un-verified'])
        except Exception as e:
            print("Exception at integrations.integrity_checks :", e)
            print(f"Skipping member {member.display_name} from checks...")
            id = str(member.id).strip().upper()
            if id in gcek_verified:
                del gcek_verified[id]

    for id in gcek_verified:
        obj = gcek_verified[id]
        DB_update(CollegeStudent, {'admn': obj.admn}, {'id': ""})

    print("DB integrity checks ended...")


async def notify_un_verified(SERVER, USER, ROLE) -> None:
    """
    Broadcast message to all un-verified
    """
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
    returns various status
    """
    ROLES = Dmember.serverRoles
    member = Dmember.memberObj
    new_id = str(member.id)

    if ROLES['verified'] in member.roles:
        return "pre-verified"
    if ROLES['GCEK-verified'] in member.roles:
        return "pre-verified"

    DB_pre_records = DB_find(CollegeStudent, id=new_id)
    if len(DB_pre_records) != 0:
        return "multiple id"

    if not Dmember.gcekian:
        await member.remove_roles(ROLES['un-verified'])
        await member.add_roles(ROLES['verified'])
        await member.edit(nick=(Dmember.name+" 🎓"))
        return 'success'

    # ADD member id in DB
    DB_pre_records = DB_find(CollegeStudent, admn=Dmember.admn)
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
    if not DB_update(CollegeStudent, {'admn': Dmember.admn}, {'id': Dmember.id}):
        return "update error"

    # update gcekian member roles:
    await member.remove_roles(ROLES['un-verified'])
    await member.add_roles(ROLES['GCEK-verified'])
    new_name = DB_pre_records[0].nickname()
    await member.edit(nick=new_name)
    return "success"


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
        print(e)
        return False
