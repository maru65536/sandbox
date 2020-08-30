import io
from PIL import Image
from selenium import webdriver
import chromedriver_binary
import json
import tweepy
from requests_oauthlib import OAuth1Session

#config.pyに入れてね！
CK = 'hoge'
CS = 'fuga'
AT = 'piyo'
ATS = 'usi'

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, ATS)
api = tweepy.API(auth)

def fetch_rate_graph(user):
    driver=webdriver.Chrome()
    driver.set_window_size(1920,1080)
    url="https://atcoder.jp/users/{:s}".format(user)
    driver.get(url)
    cvs=driver.find_element_by_css_selector("#ratingGraph")
    img=Image.open(io.BytesIO(cvs.screenshot_as_png))
    driver.close()
    return img

def graph_edit_and_save(img):
    img_x=img.size[0]
    img=img.crop((0,0,img_x,img_x//3))
    filename="img/rate_graph.png"
    img.save(filename)

def fetch_rating(user):
    driver=webdriver.Chrome()
    url="https://atcoder.jp/users/{:s}".format(user)
    driver.get(url)
    rate=int(driver.find_elements_by_class_name('user-green')[1].text)
    driver.close()
    return rate

def update_header(user,filename):
    api.update_profile_banner(filename)

def update_bio(user,rate):
    color=['灰','茶','緑','水','青','黄','橙','赤']
    api.update_profile(
        'まる',
        'https://atcoder.jp/users/maru65536',
        'う　し　た　ぷ　に　き　あ　王　国　笑',
        '男もすなる競プロといふものを男もしてみむとてするなり。'
        +'Atcoder'+color[rate//400]+'('+str(rate)+')')
    

def update_twitter(atcoder_username,twitter_username):
    filename="img/rate_graph.png"
    graph_edit_and_save(fetch_rate_graph(atcoder_username))
    update_header(twitter_username,filename)
    update_bio(twitter_username,fetch_rating(atcoder_username))

update_twitter('maru65536','maru65536_green')