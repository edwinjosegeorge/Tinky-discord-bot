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
