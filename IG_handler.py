import requests
import discord
from settings import SOCIAL_POST_CHANNEL
from SOCIAL_PSQL_hooks import DB_find, DB_find_all, DB_update_id


def extract_info(ig_username):

    data = dict()
    try:
        json_url = f"https://www.instagram.com/{ig_username}/feed/?__a=1"
        headers = {"Content-Type": "text"}
        html = requests.get(json_url, headers=headers)
        user = html.json()['graphql']['user']
        post_edges = user['edge_owner_to_timeline_media']['edges']

        data['full_name'] = user['full_name']
        data['profile_pic_url'] = user['profile_pic_url']
        data['insta_url'] = f"https://www.instagram.com/{user['username']}/"
        data['post'] = dict()

        recent_post = DB_find(ig_username)
        update_post = False
        for post in post_edges:
            if post['node']['id'] == recent_post:
                break
            if not update_post:
                update_post = DB_update_id(ig_username, post['node']['id'])

            post_data = dict()
            post_data['id'] = post['node']['id']
            post_data['display_url'] = post['node']['display_url']
            post_data['post_url'] = f"https://www.instagram.com/p/{post['node']['shortcode']}/"
            post_data['caption'] = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
            # post_data['alt_text'] = post['node']['accessibility_caption']
            data['post'][post_data['id']] = post_data
        return data
    except Exception as e:
        print(f"Exception at IG_handler.extract_info({ig_username}) : ", e)
        return data


def ig_embed_obj(ig_username):
    try:
        data = extract_info(ig_username)
        id_list = list(data['post'].keys())
        if len(id_list) == 0:
            return (False, None)

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
            return (True, embed)

        embed.set_thumbnail(url=data['post'][id]['display_url'])
        values = ""
        for id in id_list[1:]:
            desp = data['post'][id]['caption'][:30].strip().split("\n")[0]
            values += ">>"+desp+"...\n"
        embed.add_field(name="More posts you may have missed", value=values)
        return (True, embed)
    except Exception as e:
        print(f"Exception at IG_handler.ig_embed_obj({ig_username}) : ", e)
        return (False, None)


async def push_ig_embed(CLIENT):
    try:
        print("Checking for instagram updates")
        channel = CLIENT.get_channel(int(SOCIAL_POST_CHANNEL))
        for ig_username in DB_find_all():
            new_post, embed_obj = ig_embed_obj(ig_username)
            if new_post:
                print("IG embed send...")
                await channel.send(embed=embed_obj)
    except Exception as e:
        print("Exception at IG_handler.push_ig_embed : ", e)
