import requests
import asyncio
import discord
from settings import SOCIAL_POST_CHANNEL
from database.tables import Instagram
from database.hooks import DB_find, DB_update


def extract_info(ig_username: str) -> dict:
    """
    extracts info of a particular public instagram account
    """
    data = dict()
    try:
        insta_obj = DB_find(Instagram, username=ig_username)[0]
        recent_post = insta_obj.recent_post

        # get request
        json_url = f"https://www.instagram.com/{ig_username}/feed/?__a=1"
        headers = {"Content-Type": "text"}
        html = requests.get(json_url, headers=headers)
        user = html.json()['graphql']['user']
        post_edges = user['edge_owner_to_timeline_media']['edges']

        # extract data from json
        data['full_name'] = user['full_name']
        data['profile_pic_url'] = user['profile_pic_url']
        data['insta_url'] = f"https://www.instagram.com/{user['username']}/"
        data['post'] = dict()

        update_post = False
        for post in post_edges:
            if post['node']['id'] == recent_post:
                break
            if not update_post:
                update_post = DB_update(Instagram, {'username': ig_username},
                                        {'recent_post': post['node']['id']})
            post_data = dict()
            post_data['id'] = post['node']['id']
            post_data['display_url'] = post['node']['display_url']
            post_data['post_url'] = f"https://www.instagram.com/p/{post['node']['shortcode']}/"
            post_data['caption'] = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
            data['post'][post_data['id']] = post_data
        return data
    except Exception as e:
        print(f"Exception at instagram.extract_info({ig_username}) : ", e)
        return data


def embed_obj(ig_username: str):
    """
    Creates an discord.Embed object for an valid instagram account to embed
    returns embed object on successfull creation, else None
    """
    try:
        data = extract_info(ig_username)
        id_list = list(data['post'].keys())
        if len(id_list) == 0:
            return None

        id = id_list[0]
        embed = discord.Embed(title="Updates at Instagram",
                              url=data['post'][id]['post_url'],
                              description=data['post'][id]['caption'],
                              color=discord.Color.blue())
        embed.set_author(name=f"{data['full_name']} @ Instagram",
                         url=data['insta_url'],
                         icon_url=data['profile_pic_url'])

        if len(id_list) == 1:
            embed.set_image(url=data['post'][id]['display_url'])
            return embed

        embed.set_thumbnail(url=data['post'][id]['display_url'])

        values = ""
        for id in id_list[1:]:
            desp = data['post'][id]['caption'][:30].strip().split("\n")[0]
            values += ">>"+desp+"...\n"

        embed.add_field(name="More posts you may have missed", value=values)
        return embed

    except Exception as e:
        print(f"Exception at instgram.embed_obj({ig_username}) : ", e)
        return None


async def push_notification(CLIENT) -> None:
    """
    Push new updates from instagram (if any) into SOCIAL_POST_CHANNEL
    """
    try:
        channel = CLIENT.get_channel(int(SOCIAL_POST_CHANNEL))
        print("Checking for instagram updates")

        for IG_obj in DB_find(Instagram):
            new_embed_obj = embed_obj(IG_obj.username)
            if new_embed_obj is not None:
                print(f"Instagram update from {IG_obj.username}")
                await channel.send(embed=new_embed_obj)

        print("Instagram search completed")
    except Exception as e:
        print("Exception at instagram.push_notification : ", e)


async def push_notification_loop(CLIENT, time: int) -> None:
    """
    Loops instagram.push_notification with a time gap of 'time' seconds
    time >= 60 sec
    """
    if time < 60:
        time = 60
    while True:
        await push_notification(CLIENT)
        await asyncio.sleep(time)
