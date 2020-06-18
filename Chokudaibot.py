import discord
from discord.ext import tasks
import time
import datetime
from selenium import webdriver
import chromedriver_binary

# Botのアクセストークン、使用するチャンネルID、ユーザーリスト
token='hoge'
channel_id='huga'
#[DiscordID,AtCoderID]で指定。手で追加
users=[['Arice','Bob']]

client = discord.Client()

#AtCoderIDを受け取って、今日ACした問題数を返す関数
def scraping(id):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://kenkoooo.com/atcoder/#/user/{}'.format(id))
    time.sleep(3)
    ACdate=driver.find_elements_by_class_name('text-muted')[6].text
    driver.quit()
    ACY,ACM,ACD=int(ACdate[9:13]),int(ACdate[14:16]),int(ACdate[17:19])
    Nowdate=datetime.datetime.now()
    NY,NM,ND=Nowdate.year,Nowdate.month,Nowdate.day
    if ACY!=NY or ACM!=NM or ACD!=ND:
        return False
    else:
        return True

#起動時
@client.event
async def on_ready():
    loop.start()
    print('Chokudaibot起動')

# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now().strftime('%H:%M')
    if now == '20:00':
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            if scraping(person[1])==0:
                await channel.send(user.mention+' AtCoderやれ')  

# Botの起動とDiscordサーバーへの接続
client.run(token)