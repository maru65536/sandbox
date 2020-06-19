import discord
from discord.ext import tasks
import time
import datetime
import requests
from selenium import webdriver
import chromedriver_binary

# Botのアクセストークン、使用するチャンネルID、ユーザーリスト
token='NzEyMTYzMzU4Mjg3MzMxNDA5.XsNkqw.eUKp3MB20utMrDoPvzBbQG6n858'
channel_id=723157402387611748
#[DiscordID,AtCoderID]で指定。手で追加
users=[
    [414689564318498816,'maru65536'],
    [640616185137725453,'irisviel'],
    [488978370164555776,'potex59049'],
    [462862915209527298,'yi7242']
    ]

client = discord.Client()

def ACProblems(id):
    epochs=int(datetime.datetime.now().timestamp()-86400)
    AClist=[]
    url="https://kenkoooo.com/atcoder/atcoder-api/results?user={}".format(id)
    result=requests.get(url).json()
    for dic in result:
        if dic['epoch_second']>=epochs:
            AClist.append(dic["problem_id"])
    return AClist

#起動時
@client.event
async def on_ready():
    loop.start()
    print('Chokudaibot起動')

# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now().strftime('%H:%M')
    if now == '22:00':
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            AC=ACProblems(person[1])
            if len(AC)==0:
                await channel.send(user.mention+' AtCoderやれ')
            else:
                await channel.send(user.name+'は以下の{}問解きました、えらい！'.format(len(AC)))
                for Problem in AC:
                    await channel.send(Problem)

# Botの起動とDiscordサーバーへの接続
client.run(token)