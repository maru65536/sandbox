import discord
from discord.ext import tasks
import time
import math
import datetime
import requests
import json
import codecs

# Botのアクセストークン、使用するチャンネルID、ユーザーリスト
token='hoge and huga'
channel_id=723157402387611748
#[DiscordID,AtCoderID]で指定
users=[
    [414689564318498816,'maru65536','https://img.atcoder.jp/icons/285eb303e7617ede77d1176e1d000ccf.jpg'],
    [640616185137725453,'irisviel','https://img.atcoder.jp/assets/icon/avatar.png'],
    [488978370164555776,'potex59049','https://img.atcoder.jp/icons/3b54e96dcdb14dc634fd8bed931c63d3.jpg'],
    [462862915209527298,'yi7242','https://img.atcoder.jp/icons/ec72028cf0fd8fdf99d2dcfd0d33bc07.png']
    ]
colors=[0x808080,0x8b4513,0x008000,0x00ffff,0x0000ff,0xffff00,0xffa500,0xff0000]

client = discord.Client()

#AtCoderIDを入れると、ACした問題のリストを返す
#返り値は[[問題id,タイトル,diff,JOIの問題かどうか]*いくつか,maxdiff]の形
#JOIの問題である場合、diffが存在しない場合はそれぞれJOI難易度、-1を返す
#現在の時刻からsec秒前までを取得
def ACProblems(id,sec):
    epochs=int(datetime.datetime.now().timestamp()-sec)
    tmp=[]
    AC=[]
    e=math.e
    url="https://kenkoooo.com/atcoder/atcoder-api/results?user={}".format(id)
    result=requests.get(url).json()
    for dic in result:
        if dic['epoch_second']>=epochs and dic['result']=='AC':
            tmp.append([dic["problem_id"],dic["contest_id"]])
    url="https://kenkoooo.com/atcoder/resources/merged-problems.json"
    Problemlist=requests.get(url).json()
    url="https://kenkoooo.com/atcoder/resources/problem-models.json"
    difflist=requests.get(url).json()
    JOI_dic=json.load(codecs.open('Sandbox/JOI.json', 'r', 'utf-8'))
    max_diff=-(10**9)
    for problem_id in tmp:
        for dic in Problemlist:
            if problem_id[0]==dic["id"]:
                title=dic["title"]
                diff=-1
                isjoi=(problem_id[1][0:2]=='jo')
                if problem_id[0] in difflist:
                    diff=int(difflist[problem_id[0]]["difficulty"])
                #diffがマイナスにならないよう補正
                if diff<=400 and diff!=-1:
                    diff=int(400/e**((400-diff)/400))
                max_diff=max(max_diff,diff)
                JOI_title=list(title.split())[1]
                if isjoi:
                    diff=JOI_dic[JOI_title]
                AC.append([problem_id,title,diff,isjoi])
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
    #22時時点で未AC者に警告
    if now == '22:00':
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            AC=ACProblems(person[1],79200)
            if len(AC)==1:
                await channel.send(user.mention+' AtCoderやれ')
    #0時に、前日に解いた問題のリストを投稿
    elif now == '00:00':
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            AC=ACProblems(person[1],86400)
            if len(AC)==1:
                embed = discord.Embed(title=user.name, description='AtCoderやれって言ったのに...' ,color=0x000000)
                embed.set_thumbnail(url=person[2])
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(title=user.name, description='以下の{}問解きました！えらい！'.format(len(AC)-1) ,color=colors[AC[-1]//400])
                for Problem in AC:
                    if type(Problem) is int:
                        embed.set_thumbnail(url=person[2])
                        await channel.send(embed=embed)
                        break
                    embed.add_field(name=Problem[0][0],value='{} : {}{}'.format(Problem[1],'JOI難易度' if Problem[3] else 'diff',Problem[2] if Problem[2]!=-1 else 'なし'),inline=0)

# Botの起動とDiscordサーバーへの接続
client.run(token)