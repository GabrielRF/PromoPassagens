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

DESTINATION = os.environ['DESTINATION']
BOT_TOKEN = os.environ['BOT_TOKEN']
TWITTER_BEARER_TOKEN = os.environ['TWITTER_BEARER_TOKEN']
TWITTER_LIST_ID = os.environ['TWITTER_LIST_ID']

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
        img = img['content']
        preview = False
    except TypeError:
        img = ''
        preview = True
    return preview, img

def remove_urls(tweet):
    tweet = re.sub(r"(:?https?://)\S+", "", tweet)
    return tweet

if __name__ == '__main__':
    try:
        timeline = client.get_list_tweets(TWITTER_LIST_ID)
        for index in reversed(range(len(timeline))):
            btn_link = types.InlineKeyboardMarkup()
            preview = True
            tweet_text = remove_urls(timeline[index].text)
            if blocklist(tweet_text):
                break
            for word in tweet_text.split():
                if '@' in word:
                    tweet_text = tweet_text.replace(word, '')
            try:
                tweet_urls = timeline[index].entities['urls'][0]['expanded_url']
                tweet_urls = str(clean_url(clean_url(tweet_urls)))
            except KeyError:
                tweet_urls = ''
            except IndexError:
                tweet_urls = ''
            try:
                tweet_img = timeline[index].entities['media'][0]['media_url']
                preview = False
            except KeyError:
                tweet_img = ''
            hashtags = cities_hashtags(tweet_text.title())
            if len(tweet_urls) > 2:
                if len(tweet_img) < 2:
                    preview, tweet_img = get_img(tweet_urls)
                message = ('<b>' + tweet_text.strip().title() + '</b>')
                if len(hashtags)>2:
                    message = message + hashtags
                tweet_url = f'https://twitter.com/{timeline[index].user.screen_name}/status/{timeline[index].id}'
                message = f'{message}<a href="{tweet_url}">.</a>\n'
                btn = types.InlineKeyboardButton(random.choice(emoji) + ' ' + timeline[index].user.name, url=tweet_urls)
                btn_link.row(btn)
            print(tweet_url)
            if new_updates(tweet_url, get_site()):
                if not preview:
                    bot.send_photo(f'@{DESTINATION}', tweet_img, caption=message, parse_mode='HTML', reply_markup=btn_link)
                else:
                    bot.send_message(f'@{DESTINATION}', message, parse_mode='HTML', disable_web_page_preview=preview, reply_markup=btn_link)
    except Exception as error:
        print("--- Exception ---\n", error) # An exception occurred: division by zero
        pass
