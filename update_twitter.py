import io
from PIL import Image
from selenium import webdriver
import chromedriver_binary
import twitter

CONSUMER_KEY  = 'YOUR_CONSUMER_KEY'
CONSUMER_SECRET_KEY = 'YOUR_CONSUMER_SECRET_KEY'
ACCESS_TOKEN        = 'YOUR_ACCESS_TOKEN'
ACCESS_TOKEN_SECRET = 'YOUR_ACCESS_TOKEN_SECRET'

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
    rating=driver.find_elements_by_class_name('user-green')[1].text
    driver.close()
    return rating

def update_header(user,filename):
    pass

def update_bio(user,rating):
    pass

def update_twitter(atcoder_username,twitter_username):
    filename="img/rate_graph.png"
    graph_edit_and_save(fetch_rate_graph(atcoder_username))
    update_header(twitter_username,filename)
    update_bio(twitter_username,fetch_rating)

update_twitter('maru65536','maru65536_green')