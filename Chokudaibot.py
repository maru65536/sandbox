import discord #discord接続
from discord.ext import tasks #ループ処理実行
import os #カレントディレクトリ取得
import math #diff補正
import datetime #ProblemsAPI利用
import requests #ProblemsAPI利用
import json #JOI難易度表読み込み・ユーザー管理
import codecs #JOI難易度表読み込み・ユーザー管理
from selenium import webdriver #アイコン画像取得
from selenium.webdriver.chrome.options import Options #アイコン画像取得
import chromedriver_binary #アイコン画像取得

#各種変数、リストの定義
token='hoge'
channel_id=723157402387611748
hour=3600
colors=[0x000000,0x808080,0x8b4513,0x008000,0x00ffff,0x0000ff,0xffff00,0xffa500,0xff0000]
client = discord.Client()
channel = client.get_channel(channel_id)
if os.getcwd()=='C:\\VSCode\\Bots':
    Chokudaipath='Chokudai_Users.json'
else:
    Chokudaipath='Bots\\Chokudai_Users.json'
if os.getcwd()=='C:\\VSCode\\Bots':
    JOIpath='JOI.json'
else:
    JOIpath='Bots\\JOI.json'

#定期的な更新が必要なもの(問題リスト、ユーザー)
def init():
    global users,JOI_dic,Problemlist,difflist
    users=json.load(codecs.open(Chokudaipath, 'r', 'utf-8'))
    JOI_dic=json.load(codecs.open(JOIpath, 'r', 'utf-8'))
    Problemurl="https://kenkoooo.com/atcoder/resources/merged-problems.json"
    Problemlist=requests.get(Problemurl).json()
    diffurl="https://kenkoooo.com/atcoder/resources/problem-models.json"
    difflist=requests.get(diffurl).json()

#起動時に初期化
init()

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

#IDからアイコンのURLを取得
#AtCoderのユーザーページをスクレイピングする
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

# "!chokudai AtcoderID" に反応し、ユーザーリスト更新
#リストに既に存在する場合は削除
#操作後、現在の登録者リストを表示
@client.event
async def on_message(message):
    if message.content.startswith('!chokudai'):
        #エラーで停止するのを防止
        if len(list(message.content.split()))==1:
            await channel.send("error!")
            return
        ID=message.content.split()[1]
        #ユーザーリスト読み込み
        users=json.load(codecs.open(Chokudaipath, 'r', 'utf-8'))
        channel=client.get_channel(channel_id)
        #リストに存在しない場合は追加、既に存在する場合は削除
        if str(message.author.id) in users:
            del users[str(message.author.id)]
            await channel.send("{}さんをリストから削除しました。".format(ID))
        else:
            users[message.author.id]=ID
            await channel.send("{}さんをリストに登録しました。".format(ID))
        #現在の登録者を表示
        await channel.send("現在の登録者は以下の{}人です。".format(len(users)))
        for user in users.items():
            await channel.send(user[1])
        #変更を保存
        with open(Chokudaipath, 'w') as f:
            json.dump(users,f,indent=4)


# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now().strftime('%H:%M')
    #1時間ごとに生存報告
    if now[3:]=='00':
        print(now)
    #12時に各種リストの更新
    if now == "12:00":
        init()
    #20時時点で未AC者に警告
    if now == '20:00':
        for person in users.items():
            user = client.get_user(int(person[0]))
            AC=ACProblems(person[1],hour*20)
            print(person[1])
            if len(AC)==1:
                await channel.send(user.mention+' そろそろAtCoderやれ')
    #22時時点で未AC者に再警告
    elif now == "22:00":
        for person in users.items():
            user = client.get_user(int(person[0]))
            AC=ACProblems(person[1],hour*22)
            print(person[1])
            if len(AC)==1:
                await channel.send(user.mention+' いい加減AtCoderやれ')
    #0時に、前日に解いた問題のリストを投稿
    elif now == '00:00':
        for person in users.items():
            user = client.get_user(int(person[0]))
            AC=ACProblems(person[1],hour*24)
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