import discord #discord接続
from discord.ext import tasks #ループ処理実行
import math #diff補正
import datetime #ProblemsAPI利用
import requests #ProblemsAPI利用
import json #JOI難易度表読み込み
import codecs #JOI難易度表読み込み
from selenium import webdriver #アイコン画像取得
from selenium.webdriver.chrome.options import Options #アイコン画像取得
import chromedriver_binary #アイコン画像取得

# Botのアクセストークン、使用するチャンネルID、ユーザーリスト
token='NzEyMTYzMzU4Mjg3MzMxNDA5.Xu5Ang.fl3s9sXYZjfH2V0G1OFe4ULyaXs'
channel_id=723157402387611748
#[DiscordID,AtCoderID,画像URL]
users=[
    [414689564318498816,'maru65536'],
    [640616185137725453,'irisviel'],
    [462862915209527298,'yi7242'],
    [488978370164555776,'potex59049']
]
colors=[0x000000,0x808080,0x8b4513,0x008000,0x00ffff,0x0000ff,0xffff00,0xffa500,0xff0000]

client = discord.Client()

#AtCoderIDを入れると、ACした問題のリストを返す
#返り値は[[問題id,タイトル,diff,JOIの問題かどうか]*問題数,maxdiff]の形
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
            if [dic["problem_id"],dic["contest_id"]] not in tmp:
                tmp.append([dic["problem_id"],dic["contest_id"]])
    url="https://kenkoooo.com/atcoder/resources/merged-problems.json"
    Problemlist=requests.get(url).json()
    url="https://kenkoooo.com/atcoder/resources/problem-models.json"
    difflist=requests.get(url).json()
    JOI_dic=json.load(codecs.open('Sandbox/JOI.json', 'r', 'utf-8'))
    max_diff=-1
    for problem_id in tmp:
        for dic in Problemlist:
            #解いた問題についてProblemlistの該当箇所を見つける
            if problem_id[0]==dic["id"]:
                title=dic["title"]
                diff=-1
                isjoi=(problem_id[1][0:2]=='jo')
                #難易度を取得
                if problem_id[0] in difflist:
                    if "difficulty" in difflist[problem_id[0]]:
                        diff=int(difflist[problem_id[0]]["difficulty"])
                #diffがマイナスにならないよう補正
                if diff<=400 and diff!=-1:
                    diff=int(400/e**((400-diff)/400))
                max_diff=max(max_diff,diff)
                #JOI難易度が存在すれば取得
                JOI_title=list(title.split())[1]
                if len(list(title.split()))>2:
                    JOI_title2=list(title.split())[1]+list(title.split())[2]
                if isjoi:
                    if JOI_title in JOI_dic:
                        diff=JOI_dic[JOI_title]
                    elif JOI_title2 in JOI_dic:
                        diff=JOI_dic[JOI_title2]
                AC.append([problem_id,title,diff,isjoi])
                continue
    #ソート、最高diffを追加して返す
    AC.sort(key=lambda x:(-x[3],x[2]),reverse=True)
    AC.append(max_diff)
    return AC

def fetch_icon(id):
    options = Options()
    options.add_argument('--headless')
    driver=webdriver.Chrome(options=options)
    url="https://atcoder.jp/users/{:s}".format(id)
    driver.get(url)
    img=driver.find_element_by_class_name('avatar').get_attribute("src")
    driver.close()
    return img

#起動時
@client.event
async def on_ready():
    loop.start()
    print('Chokudaibot起動')

# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now().strftime('%H:%M')
    #20時時点で未AC者に警告
    if now == '20:00':
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            AC=ACProblems(person[1],72000)
            print(person[1])
            if len(AC)==1:
                await channel.send(user.mention+' そろそろAtCoderやれ')
    #22時時点で未AC者に再警告
    elif now == "22:00":
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            AC=ACProblems(person[1],79200)
            print(person[1])
            if len(AC)==1:
                await channel.send(user.mention+' いい加減AtCoderやれ')
    #0時に、前日に解いた問題のリストを投稿
    elif now == '00:00':
        channel = client.get_channel(channel_id)
        for person in users:
            user = client.get_user(person[0])
            AC=ACProblems(person[1],86400)
            print(person[1])
            AC[-1]+=400
            color=colors[AC[-1]//400]
            if len(AC)==1: #AC数0(ACがmax_difficultyのみ)
                embed = discord.Embed(title=user.name, description='AtCoderやれって言ったのに...' ,color=color)
                embed.set_thumbnail(url=fetch_icon(person[1]))
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(title=user.name, description='以下の{}問解きました！えらい！'.format(len(AC)-1) ,color=color)
                embed.set_thumbnail(url=fetch_icon(person[1]))
                i=0
                for Problem in AC:
                    if i==25: #一回の投稿は25が限界なので区切る
                        i=0
                        await channel.send(embed=embed)
                        embed = discord.Embed(title=user.name, description='つづき',color=color)
                    if type(Problem) is int: #終端(max_difficulty)なら終了
                        embed.set_thumbnail(url=fetch_icon(person[1]))
                        await channel.send(embed=embed)
                        break
                    else:
                        index='JOI難易度' if Problem[3] else 'diff'
                        diff=Problem[2] if Problem[2]!=-1 else 'なし'
                        embed.add_field(name=Problem[0][0],value='{} : {}{}'.format(Problem[1],index,diff),inline=False)
                    i+=1

#Botの起動とDiscordサーバーへの接続
client.run(token)