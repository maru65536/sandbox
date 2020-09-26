import codecs #JOI難易度表読み込み・ユーザー管理
import datetime #ProblemsAPI用の時刻取得
import json #JOI難易度表読み込み・ユーザー管理
from math import e #diff補正
import os #カレントディレクトリ取得

import bs4 #コード取得
import chromedriver_binary #アイコン画像取得
import discord #discord接続
from discord.ext import tasks #ループ処理実行
import requests #ProblemsAPI利用
from selenium import webdriver #アイコン画像取得
from selenium.webdriver.chrome.options import Options #アイコン画像取得
import chromedriver_binary #アイコン画像取得


#各種、更新の必要がない変数の定義
token='hoge'
channel_id=723157402387611748
hour=3600
colors=[0x000000,0x808080,0x8b4513,0x008000,0x00ffff,0x0000ff,0xffff00,0xffa500,0xff0000]
client = discord.Client()


class problems():
    def __init__(self):
        self.l=[]

    def add_problem(self,ID,title,difficulty,isJOI,submit_id):
        self.l.append([ID,title,difficulty,isJOI,submit_id])

    def max_difficulty(self):
        self.diffs=[Problem[2] for Problem in self.l if not Problem[3]]
        if len(self.diffs)==0:
            return -1
        return max(self.diffs)

    def ac_list(self):
        return sorted(self.l,key=lambda x: (x[3],-x[2]))

    def ac_count(self):
        return len(self.l)


#動かす場所によって相対パスを変える
if os.getcwd()=='C:\\VSCode\\Bots':
    Userspath='Chokudai_Users.json'
else:
    Userspath='Bots\\Chokudai_Users.json'
if os.getcwd()=='C:\\VSCode\\Bots':
    JOIpath='JOI.json'
else:
    JOIpath='Bots\\JOI.json'


#定期的な更新が必要な変数を定義(問題リスト、ユーザー)
def init():
    global users,JOI_dic,Problemlist,difflist,Contestlist
    users=json.load(codecs.open(Userspath, 'r', 'utf-8'))
    JOI_dic=json.load(codecs.open(JOIpath, 'r', 'utf-8'))
    Problemurl="https://kenkoooo.com/atcoder/resources/merged-problems.json"
    Problemlist=requests.get(Problemurl).json()
    diffurl="https://kenkoooo.com/atcoder/resources/problem-models.json"
    difflist=requests.get(diffurl).json()
    Contesturl="https://kenkoooo.com/atcoder/resources/contests.json"
    Contestlist=requests.get(Contesturl).json()


#AtCoderIDを入れると、ACした問題のリストを返す
#返り値は[[問題id,タイトル,diff,JOIの問題かどうか]*問題数,maxdiff]の形
#JOIの問題である場合、diffが存在しない場合はそれぞれJOI難易度、-1を返す
#現在の時刻からsec秒前までを取得
def ACProblems(id,sec):
    epochs,p,tmp=int(datetime.datetime.now().timestamp()-sec),problems(),[]
    url="https://kenkoooo.com/atcoder/atcoder-api/results?user={}".format(id)
    result=requests.get(url).json()
    for dic in result:
        if dic['epoch_second']>=epochs and dic['result']=='AC':
            if [dic["problem_id"],dic["contest_id"]] not in tmp:
                tmp.append([dic["problem_id"],dic["contest_id"],dic['id']])
    #解いた問題について、各データを取得
    for problem_id,contest_id,submit_id in tmp:
        for dic in Problemlist:
            if problem_id==dic["id"]:
                title=dic["title"]
                titles=list(title.split())
                diff=-1
                isjoi=(contest_id[0:2]=='jo')
                #難易度を取得
                if problem_id in difflist:
                    if "difficulty" in difflist[problem_id]:
                        diff=int(difflist[problem_id]["difficulty"])
                #diffがマイナスにならないよう補正
                if diff<=400 and diff!=-1:
                    diff=int(400/e**((400-diff)/400))
                #JOI難易度が存在すれば取得
                JOI_title=titles[1]
                if len(titles)>2:
                    JOI_title2=titles[1]+titles[2]
                if isjoi:
                    if JOI_title in JOI_dic:
                        diff=int(JOI_dic[JOI_title])
                    elif JOI_title2 in JOI_dic:
                        diff=int(JOI_dic[JOI_title2])
                p.add_problem(problem_id,title,diff,isjoi,submit_id)
    return p


#IDからアイコンのURLを取得
#AtCoderのユーザーページをスクレイピングする
#ユーザーが存在しない場合は-1を返す
def fetch_icon(id):
    try:
        options = Options()
        options.add_argument('--headless')
        driver=webdriver.Chrome(options=options)
        url="https://atcoder.jp/users/{:s}".format(id)
        driver.get(url)
        img=driver.find_element_by_class_name('avatar').get_attribute("src")
        driver.close()
        return img
    except:
        return -1


#実装する！(素振り)
def Current_Streak(id):
    pass


#起動時
@client.event
async def on_ready():
    print('Chokudai OK')
    init()
    loop.start()


@client.event
async def on_message(message):
    #ユーザー登録・登録解除
    #"!chokudai regi (AtCoderID)"でユーザーリストに登録される
    #ユーザーリストに既に存在しない場合は削除される
    if message.content.startswith('!chokudai regi'):
        #ユーザーリスト・チャンネル読み込み
        users=json.load(codecs.open(Userspath, 'r', 'utf-8'))
        channel=client.get_channel(channel_id)
        #エラーで停止するのを防止
        if len(list(message.content.split()))!=3:
            await channel.send("error!")
            return
        ID=message.content.split()[2]
        if fetch_icon(ID)==-1:
            await channel.send('無効なIDです')
            return
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
        with open(Userspath, 'w') as f:
            json.dump(users,f,indent=4)

    #指定した人間のAC状況の表示(DMのみ対応)
    #"!chokudai display (AtCoderID) (hours)"で、IDが現在からhours時間以内にACした問題を表示
    if message.content.startswith('!chokudai display'):
        channel=client.get_user(message.author.id)
        content=list(message.content.split())
        l=len(content)
        #遡る秒数を設定
        if l==3:
            sec=86400
        elif l==4:
            sec=int(float(content[3])*hour)
        else:
            channel.send('Error!')
            return
        ID=content[2]
        problems=ACProblems(ID,sec)
        color=colors[problems.max_difficulty()//400+1]
        icon_url=fetch_icon(ID)
        if icon_url==-1:
            await channel.send('無効なIDです')
        if problems.ac_count()==0: #AC数0の場合
                embed = discord.Embed(title=ID, description='AtCoderをしていません' ,color=color)
                embed.set_thumbnail(url=icon_url)
                await channel.send(embed=embed)
        else:
            embed = discord.Embed(title=ID, description='以下の{}問解きました！'.format(problems.ac_count()) ,color=color)
            embed.set_thumbnail(url=icon_url)
            i=0
            for ID,title,difficulty,isJOI,_ in problems.ac_list():
                if i==25: #一回の投稿は25が限界なので区切る
                    i=0
                    await channel.send(embed=embed)
                    embed = discord.Embed(title=user.name, description='つづき',color=color)
                index='JOI難易度' if isJOI else 'diff'
                diff=difficulty if difficulty!=-1 else 'なし'
                embed.add_field(name=ID,value='{} : {}{}'.format(title,index,diff),inline=False)
                i+=1
            await channel.send(embed=embed)

    #helpで、現在実装されている命令をすべて表示
    if message.content.startswith('!chokudai help'):
        channel=client.get_channel(channel_id)
        await channel.send('"help" でhelpを表示')
        await channel.send('"!chokudai regi (AtCoderID)"でユーザーリストに登録')
        await channel.send('ユーザーリストに既に存在しない場合は削除される')
        await channel.send('DMに"!chokudai display (AtCoderID) (hours)"で、指定した人が現在からhours時間以内にACした問題をDMに送信')
        await channel.send('hoursが指定されなかった場合はデフォルトで24時間以内のACを表示する')

    #隠しコマンド、bibleで例のツイートを表示
    if message.content.startswith('!chokudai bible'):
        channel=client.get_channel(channel_id)
        await channel.send('だから慶應は学歴自慢じゃないっつーの。')
        await channel.send('慶應という学歴が俺を高めるんじゃない。俺という存在が慶應という学歴の価値を高めるんだよ。')
        await channel.send('https://twitter.com/chokudai/status/680773059410702337')


# 60秒に一回ループ
@tasks.loop(seconds=60)
async def loop():
    now = datetime.datetime.now().strftime('%H:%M')
    channel = client.get_channel(channel_id)
    #1時間ごとに生存報告、リストの初期化
    if now[3:]=='00':
        print(now)
        init()
    #20時時点で未AC者に警告
    if now == "20:00":
        for discord_id,atcoder_id in users.items():
            user = client.get_user(int(discord_id))
            problems=ACProblems(atcoder_id,hour*20)
            if problems.ac_count()==0:
                await channel.send(user.mention+' そろそろAtCoderやれ')
    #22時時点で未AC者に再警告
    elif now == "22:00":
        for discord_id,atcoder_id in users.items():
            user = client.get_user(int(discord_id))
            problems=ACProblems(atcoder_id,hour*22)
            if problems.ac_count()==0:
                await channel.send(user.mention+' いい加減AtCoderやれ')
    #0時に、前日に解いた問題のリストを投稿
    #コンテストのある日はProblemsのスクレイピングを待って1時に投稿する
    elif now == "00:00":
        for discord_id,atcoder_id in users.items():
            user = client.get_user(int(discord_id))
            problems=ACProblems(atcoder_id,hour*(24))
            color=colors[problems.max_difficulty()//400+1]
            icon_url=fetch_icon(atcoder_id)
            if problems.ac_count()==0: #AC数0の場合
                embed = discord.Embed(title=user.name, description='AtCoderやれって言ったのに...' ,color=color)
                embed.set_thumbnail(url=icon_url)
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(title=user.name, description='以下の{}問解きました！えらい！'.format(problems.ac_count()) ,color=color)
                embed.set_thumbnail(url=icon_url)
                i=0
                for ID,title,difficulty,isJOI,_ in problems.ac_list():
                    if i==25: #一回の投稿は25が限界なので区切る
                        i=0
                        await channel.send(embed=embed)
                        embed = discord.Embed(title=user.name, description='つづき',color=color)
                    index='JOI難易度' if isJOI else 'diff'
                    diff=difficulty if difficulty!=-1 else 'なし'
                    embed.add_field(name=ID,value='{} : {}{}'.format(title,index,diff),inline=False)
                    i+=1
                await channel.send(embed=embed)
        channel=client.get_user(414689564318498816)
        for ID,title,difficulty,isJOI,submit_id in ACProblems('mdk_51',86400).ac_list():
            index='JOI難易度' if isJOI else 'diff'
            diff=difficulty if difficulty!=-1 else 'なし'
            ID=list(ID.split('_'))
            if ID[0][:2]=='jo':
                ID=ID[0]+ID[1]
            else:
                ID=ID[0]
            url='https://atcoder.jp/contests/{}/submissions/{}'.format(ID,submit_id)
            res=requests.get(url)
            soup=bs4.BeautifulSoup(res.text,'html.parser')
            code=list(soup.find(id='submission-code').get_text().split('\n'))
            count=(len(code)-1)//10+1
            await channel.send('{} : {}{}'.format(title,index,diff))
            await channel.send(url)
            for i in range(count):
                await channel.send('```C++\n'+''.join(code[i*10:min(i*10+10,len(code))])+'```')


#Botの起動とDiscordサーバーへの接続
client.run(token)