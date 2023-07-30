from bs4 import BeautifulSoup
import configparser
from telebot import types
import os
import random
import re
import requests
import telebot
import tweepy
import urllib

def get_variable(variable):
    if not os.environ.get(f'{variable}'):
        var_file = open(f'{variable}.txt', 'r')
        return var_file.read().replace('\n', '')
    return os.environ.get(f'{variable}')

DESTINATION = get_variable('DESTINATION')
BOT_TOKEN = get_variable('BOT_TOKEN')
TWITTER_BEARER_TOKEN = get_variable('TWITTER_BEARER_TOKEN')
TWITTER_LIST_ID = get_variable('TWITTER_LIST_ID')
print(DESTINATION)

client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)

emoji = [str(u'\U0001F30D'), str(u'\U0001F30E'), str(u'\U0001F30F'), str(u'\U00002708'), str(u'\U0001F680'), str(u'\U0001F4A5'), str(u'\U0001F5FB'), str(u'\U0001F5FC'), str(u'\U0001F5FD'), str(u'\U0001F310')]

def clean_url(url):
    request = requests.Session()
    request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    response = request.get(url)
    return response.url

def get_site():
    response = requests.get(f'https://t.me/s/{DESTINATION}')
    if response.status_code != 200:
        return False
    return BeautifulSoup(response.content, 'html.parser')

def new_updates(text, html):
    if text not in str(html):
        return True
    return False

def cities_hashtags(tweet):
    hashtag = ''
    city_file = open('cities.txt', 'r')
    for city in city_file.readlines():
        if city.replace('\n','') in tweet:
            hashtag = hashtag + ' #' + city.replace('\n','').replace(' ','_').replace('.','')
    return hashtag

def blocklist(tweet):
    blocklist = open('blocklist.txt', 'r')
    for word in blocklist.readlines():
        if word.replace('\n','') in tweet:
            return True
    return False

def get_img(url):
    response = requests.get(url, headers = {'User-agent': 'Mozilla/5.1'})
    html = BeautifulSoup(response.content, 'html.parser')
    img = html.find('meta', {'property': 'og:image'})
    if not img:
        img = html.find('meta', {'name': 'og:image'})
    try:
        photo = img['content']
    except TypeError:
        photo = False
    return photo

def remove_urls(tweet):
    tweet = re.sub(r"(:?https?://)\S+", "", tweet)
    return tweet

if __name__ == '__main__':
    timeline = client.get_list_tweets(
        TWITTER_LIST_ID,
        max_results=5,
        expansions=['author_id', 'attachments.media_keys'],
        media_fields=['preview_image_url'],
        tweet_fields=['context_annotations', 'created_at'],
    ).data
    for tweet in timeline:
        print(tweet['id'])
        urls = []
        tweet_text = remove_urls(tweet["text"]).title()
        if blocklist(tweet_text):
            break
        img_url = f'https://fxtwitter.com/Metropoles/status/{tweet["id"]}'
        hashtags = cities_hashtags(tweet_text.title())
        for word in tweet["text"].split():
            if 'https' in word:
                urls.append(word)
        if len(urls) < 1:
            continue
        #try:
        #    btn_link = urls[0]
        #except IndexError:
        #    btn_link = False
        #try:
        #    photo = urls[1]
        #except IndexError:
        #    photo = False
        #if not photo and len(urls) == 1:
        photo = get_img(urls[-1])
        btn_link = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(random.choice(emoji) + ' Abrir post', url=urls[0])
        btn_link.row(btn)
        if not new_updates(urls[0], get_site()):
            continue
        if photo:
            bot.send_photo(f'@{DESTINATION}', photo, caption=f'<b>{tweet_text}</b>\n{hashtags}', parse_mode='HTML', reply_markup=btn_link)
        else:
            bot.send_message(f'@{DESTINATION}', tweet_text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=btn_link)
