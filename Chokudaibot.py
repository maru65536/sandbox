import discord
from discord.ext import tasks
import time
import math
import datetime
import requests

# Botのアクセストークン、使用するチャンネルID、ユーザーリスト
token='hoge and huga'
channel_id=723157402387611748
#[DiscordID,AtCoderID]で指定。手で追加
users=[
    [414689564318498816,'maru65536'],
    [640616185137725453,'irisviel'],
    [488978370164555776,'potex59049'],
    [462862915209527298,'yi7242']
    ]


client = discord.Client()

def ACProblems(id,sec):
    epochs=int(datetime.datetime.now().timestamp()-sec)
    tmp=[]
    AC=[]
    e=math.e
    url="https://kenkoooo.com/atcoder/atcoder-api/results?user={}".format(id)
    result=requests.get(url).json()
    for dic in result:
        if dic['epoch_second']>=epochs and dic['result']=='AC':
            tmp.append(dic["problem_id"])
    url="https://kenkoooo.com/atcoder/resources/merged-problems.json"
    Problemlist=requests.get(url).json()
    url="https://kenkoooo.com/atcoder/resources/problem-models.json"
    difflist=requests.get(url).json()
    max_diff=-(10**9)
    for problem_id in tmp:
        for dic in Problemlist:
            if problem_id==dic["id"]:
                title=dic["title"]
                diff=-1
                if problem_id in difflist:
                    diff=int(difflist[problem_id]["difficulty"])
                if diff<=400 and diff!=-1:
                    diff=int(400/e**((400-diff)/400))
                max_diff=max(max_diff,diff)
                AC.append([problem_id,title,diff])
                continue
    AC.append(max_diff)
    return AC

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
            AC=ACProblems(person[1],79200)
            if len(AC)==1:
                await channel.send(user.mention+' AtCoderやれ')
    elif now == '00:00':
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            AC=ACProblems(person[1],86400)
            if len(AC)==1:
                await channel.send(user.name+'、AtCoderやれって言ったのに...')
            else:
                await channel.send(user.name+'は以下の{}問を解きました、えらい！'.format(len(AC)-1))
                for Problem in AC:
                    if type(Problem) is int:
                        await channel.send('max_diff:'+(str(AC[-1]) if AC[-1]!=-1 else 'なし'))
                        break
                    await channel.send('ID:{}  title:{}  diff:{}'.format(Problem[0],Problem[1],Problem[2] if Problem[2]!=-1 else 'なし'))

# Botの起動とDiscordサーバーへの接続
client.run(token)