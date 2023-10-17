import feedparser
import os
import random
import requests
import sqlite3
import telebot
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

def send_message(post, message, button):
    emoji = ['✈️','🧳','🛩','🚞','🚢','🏝','🗺','💺','🧭']
    bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
    bot.send_photo(
        os.environ.get('DESTINATION'),
        post['photo'],
        caption=f'{random.choice(emoji)} {message.title()}',
        parse_mode='HTML',
        reply_markup=button
    )

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
        post['photo'] = get_post_photo(post['link'])
        message, button = create_post(post)
        try:
            send_message(post, message, button)
        except Exception as e:
            print(e)
        add_to_history(post['link'])

if __name__ == "__main__":
    get_feed(os.environ.get('URL'))
