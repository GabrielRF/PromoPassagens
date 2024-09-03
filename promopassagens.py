import feedparser
import os
import random
import requests
import sqlite3
import telebot
from atproto import Client, client_utils
from bs4 import BeautifulSoup
from telebot import types

def add_to_history(link):
    conn = sqlite3.connect('links_history.db')
    cursor = conn.cursor()
    aux = f'INSERT INTO history (link) VALUES ("{link}")'
    cursor.execute(aux)
    conn.commit()
    conn.close()

def in_history(link):
    conn = sqlite3.connect('links_history.db')
    cursor = conn.cursor()
    aux = f'SELECT * from history WHERE link="{link}"'
    cursor.execute(aux)
    data = cursor.fetchone()
    conn.close()
    return data

def blocklist(text):
    blocklist = open('blocklist.txt', 'r')
    for word in blocklist.readlines():
        if word.replace('\n','') in text:
            return True
    return False

def get_post_photo(url):
    response = requests.get(
        url,
        headers = {'User-agent': 'Mozilla/5.1'},
        timeout=3
    )
    html = BeautifulSoup(response.content, 'html.parser')
    photo = html.find('meta', {'property': 'og:image'})['content']
    return photo

def cities_hashtags(text):
    hashtag = ''
    city_file = open('cities.txt', 'r')
    for city in city_file.readlines():
        if city.replace('\n','').title() in text:
            hashtag = hashtag + ' #' + city.replace('\n','').replace(' ','_').replace('.','')
    return hashtag

def create_post(post):
    message = (
        f'<b>{post["title"]}</b>\n'
        f'{cities_hashtags(post["title"])}'
    )
    btn_link = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        f'🔗 {post["author"]}',
        url=post['link'])
    btn_link.row(btn)
    return message, btn_link

def add_reaction(msg):
    reactions = ['👍','❤️','🔥','🥰','👏','🤯','🤩']
    react = random.choice(reactions)
    bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
    bot.set_message_reaction(
        msg.chat.id,
        msg.message_id,
        [telebot.types.ReactionTypeEmoji(react)]
    )

def send_bluesky(post):
    emoji = ['✈️','🧳','🛩 ','🚞','🚢','🏝 ','🗺 ','💺','🧭']
    client = Client(base_url='https://bsky.social')
    client.login('promopassagens.grf.xyz', os.environ.get('BLUESKY_PASSWORD'))

    request = requests.get(post['photo'], stream=True)
    file_name = f'{post["photo"].split("/")[-1].split("?")[0]}'
    with open(file_name, 'wb') as image:
        for chunk in request:
            image.write(chunk)
    with open (file_name, 'rb') as f:
        image_data = f.read()

    text_builder = client_utils.TextBuilder()
    text_builder.link(
        f'{random.choice(emoji)} {post["author"]}\n{post["title"]}',
        post["link"]
    )

    client.send_image(
        text=text_builder,
        image=image_data,
        image_alt=post['title'],
    )
    os.remove(file_name)

def send_message(post, message, button):
    emoji = ['✈️','🧳','🛩','🚞','🚢','🏝','🗺','💺','🧭']
    bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
    msg = bot.send_photo(
        os.environ.get('DESTINATION'),
        post['photo'],
        caption=f'{random.choice(emoji)} {message.title()}',
        parse_mode='HTML',
        reply_markup=button
    )
    add_reaction(msg)

def get_feed(url):
    feed = feedparser.parse(url)
    for pst in feed['items'][:5]:
        post = {}
        post['author'] = feed['feed']['title']
        post['link'] = pst.links[0].href
        if in_history(post['link']):
            continue
        post['title'] = pst.title.strip().title()
        if blocklist(post['title']):
            continue
        try:
            post['photo'] = get_post_photo(post['link'])
        except:
            continue
        message, button = create_post(post)
        try:
            send_message(post, message, button)
        except Exception as e:
            print(f'Link: {pst.links[0].href}\nErro: {e}')
        try:
            send_bluesky(post)
        except:
            pass
        add_to_history(post['link'])

if __name__ == "__main__":
    get_feed(os.environ.get('URL'))
