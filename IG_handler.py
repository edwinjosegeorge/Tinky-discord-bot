import requests
import discord

INSTAGRAM_USERNAME = "tinkerhub.gcek"


def get_instagram_html(INSTAGRAM_USERNAME):
    json_url = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/feed/?__a=1"
    headers = {"Content-Type": "text"}
    html = requests.get(json_url, headers=headers)
    return html


def extract_info(html):
    user = html.json()['graphql']['user']
    post_edges = user['edge_owner_to_timeline_media']['edges']

    data = dict()
    data['full_name'] = user['full_name']
    data['profile_pic_url'] = user['profile_pic_url']
    data['insta_url'] = f"https://www.instagram.com/{user['username']}/"
    data['post'] = dict()

    for post in post_edges:
        post_data = dict()
        post_data['id'] = post['node']['id']
        post_data['display_url'] = post['node']['display_url']
        post_data['post_url'] = f"https://www.instagram.com/p/{post['node']['shortcode']}/"
        post_data['caption'] = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
        # post_data['alt_text'] = post['node']['accessibility_caption']
        data['post'][post_data['id']] = post_data
    return data


def embed():
    data = extract_info(get_instagram_html('tinkerhub'))
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
