import requests

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
    data['username'] = user['username']
    data['post'] = dict()
    for post in post_edges:
        post_data = dict()
        post_data['id'] = post['node']['id']
        post_data['shortcode_url'] = f"https://www.instagram.com/p/{post['node']['shortcode']}/"
        post_data['alt_text'] = post['node']['accessibility_caption']
        post_data['caption'] = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
        post_data['display_url'] = post['node']['display_url']
        data['post'][post_data['id']] = post_data
    return data
